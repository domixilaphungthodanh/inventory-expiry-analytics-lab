from datetime import date, timedelta

import pandas as pd

from .db import TABLES
from .fefo import simulate
from .sql_metrics import sql_tables


def pandas_tables(connection, as_of):
    raw = {name: pd.read_sql_query(f"SELECT * FROM {name} ORDER BY 1", connection) for name in TABLES}
    products = raw["products"]
    moves = raw["stock_movements"]
    moves = moves[moves.occurred_at.str[:10].le(as_of)].copy()
    signed = moves.quantity.where(moves.kind.eq("receipt"), -moves.quantity)
    stock = signed.groupby(moves.lot_id).sum().rename("on_hand")
    lots = raw["lots"].merge(stock, on="lot_id").merge(products, on="product_id")
    lots = lots[["lot_id","product_id","name","unit","received_on","expires_on","on_hand"]]
    within = (date.fromisoformat(as_of) + timedelta(days=7)).isoformat()
    lots["status"] = "valid"
    lots.loc[lots.expires_on.le(within),"status"] = "expiring"
    lots.loc[lots.expires_on.lt(as_of),"status"] = "expired"
    lots.loc[lots.on_hand.eq(0),"status"] = "empty"
    totals = lots.assign(eligible=lots.on_hand.where(lots.expires_on.ge(as_of),0),
                         expired=lots.on_hand.where(lots.expires_on.lt(as_of),0))
    totals = totals.groupby("product_id")[["on_hand","eligible","expired"]].sum()
    moves = moves.merge(raw["lots"][["lot_id","product_id"]], on="lot_id").merge(
        products[["product_id","unit"]], on="product_id").sort_values(["occurred_at","movement_id"])
    return dict(lots=lots, products=products.join(totals,on="product_id").fillna(0),
                expiring=lots[lots.status.eq("expiring")], expired=lots[lots.status.eq("expired")],
                movements=moves,
                quality=pd.DataFrame([(name,len(raw[name])) for name in TABLES],columns=["table","rows"]))


def verify_allocation(connection, lots, product, quantity, as_of):
    actual, shortage = simulate(connection, product, quantity, as_of)
    candidates = lots[lots.product_id.eq(product) & lots.expires_on.ge(as_of) & lots.on_hand.gt(0)]
    remaining = quantity
    expected = []
    for row in candidates.sort_values(["expires_on","received_on","lot_id"]).itertuples():
        allocated = min(remaining, row.on_hand)
        if not allocated:
            break
        expected.append((row.lot_id, allocated))
        remaining -= allocated
    if list(zip(actual.lot_id, actual.allocated)) != expected or shortage != remaining:
        raise ValueError("SQL và pandas không khớp ở mô phỏng FEFO")
    return actual, shortage


def checked_tables(connection, as_of):
    sql = sql_tables(connection, as_of)
    independent = pandas_tables(connection, as_of)
    for name, table in sql.items():
        pd.testing.assert_frame_equal(table.reset_index(drop=True),
                                      independent[name].reset_index(drop=True),
                                      check_dtype=False, check_exact=True, obj=name)
    return sql


