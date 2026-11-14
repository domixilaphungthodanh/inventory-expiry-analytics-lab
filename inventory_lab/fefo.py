import pandas as pd

from .db import observation
from .sql_metrics import query


def simulate(connection, product, quantity, as_of):
    if type(quantity) is not int or not 1 <= quantity <= 2**63 - 1:
        raise ValueError("Số lượng phải là số nguyên dương trong phạm vi SQLite")
    if not connection.execute("SELECT 1 FROM products WHERE product_id=?", (product,)).fetchone():
        raise ValueError("Không tìm thấy mặt hàng")
    rows = pd.read_sql_query(query("fefo").format(balances=query("balances")), connection,
                             params={"product": product, "quantity": quantity,
                                     "as_of": observation(as_of)})
    return rows, quantity - sum(rows.allocated)

