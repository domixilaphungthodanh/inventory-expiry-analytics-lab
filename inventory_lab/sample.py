from datetime import date, timedelta
import random

from .db import FIRST, LAST, ROOT


def populate(connection):
    rng = random.Random(42)
    first = date.fromisoformat(FIRST)
    connection.executescript((ROOT / "sql/schema.sql").read_text(encoding="utf-8"))
    with connection:
        connection.executemany("INSERT INTO products VALUES(?,?,?)",
                               [(i, f"Mặt hàng mẫu {i:02}", "gói" if i % 2 == 0 else "hộp")
                                for i in range(1, 25)])
        connection.executemany("INSERT INTO metadata VALUES(?,?)",
                               [("seed","42"), ("timezone","Asia/Ho_Chi_Minh"),
                                ("source","Giả lập"), ("as_of",LAST), ("schema_version","1")])
        movements = []
        for i in range(120):
            lot = f"L{i + 1:03}"
            product = i % 24 + 1
            received = first + timedelta(days=i % 60)
            expires = received + timedelta(days=rng.randint(12, 105))
            if i in (0, 24):
                expires = date(2026, 3, 31)
            quantity = rng.randint(20, 65)
            connection.execute("INSERT INTO lots VALUES(?,?,?,?)",
                               (lot, product, received.isoformat(), expires.isoformat()))
            movements.append((lot, f"{received} 07:00:00", "receipt", quantity))
            for day in (1, 3, 7, 10):
                issued = quantity - 3 if i == 2 and day == 10 else rng.randint(1, 4)
                if i == 2 and day != 10:
                    issued = 1
                movements.append((lot, f"{received + timedelta(days=day)} 09:00:00", "issue", issued))
        movements.sort(key=lambda row: (row[1], row[0]))
        connection.executemany("INSERT INTO stock_movements(lot_id,occurred_at,kind,quantity) VALUES(?,?,?,?)",
                               movements)

