import pandas as pd

from .db import ROOT, TABLES, observation
from .prepare_data import validate


def query(name):
    return (ROOT / f"sql/{name}.sql").read_text(encoding="utf-8")


def snapshot(connection, as_of):
    return pd.read_sql_query(f"WITH balances AS ({query('balances')}) {query('status')}",
                             connection, params={"as_of": observation(as_of)})


def sql_tables(connection, as_of):
    counts = validate(connection)
    lots = snapshot(connection, as_of)
    products = pd.read_sql_query(f"""
        WITH balances AS ({query('balances')}), totals AS (
            SELECT product_id,SUM(on_hand) AS on_hand,
                   SUM(CASE WHEN expires_on >= :as_of THEN on_hand ELSE 0 END) AS eligible,
                   SUM(CASE WHEN expires_on < :as_of THEN on_hand ELSE 0 END) AS expired
            FROM balances GROUP BY product_id
        )
        SELECT p.*,COALESCE(on_hand,0) AS on_hand,COALESCE(eligible,0) AS eligible,
               COALESCE(expired,0) AS expired
        FROM products p LEFT JOIN totals USING(product_id) ORDER BY product_id
    """, connection, params={"as_of": as_of})
    movements = pd.read_sql_query("""
        SELECT m.*,l.product_id,p.unit FROM stock_movements m
        JOIN lots l USING(lot_id) JOIN products p USING(product_id)
        WHERE occurred_at < date(?,'+1 day') ORDER BY occurred_at,movement_id
    """, connection, params=(as_of,))
    quality = pd.DataFrame([(table, counts[table]) for table in TABLES], columns=["table", "rows"])
    return dict(lots=lots, products=products, expiring=lots[lots.status.eq("expiring")],
                expired=lots[lots.status.eq("expired")], movements=movements, quality=quality)

