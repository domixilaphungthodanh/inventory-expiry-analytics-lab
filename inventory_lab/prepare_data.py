import argparse
import csv
from datetime import date, datetime
import os
from pathlib import Path
import tempfile

from .db import DEFAULT_DB, FIRST, LAST, ROOT, TABLES, connect
from .sample import populate


def validate(connection):
    if connection.execute("PRAGMA foreign_key_check").fetchone():
        raise ValueError("Khóa ngoại không hợp lệ")
    if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise ValueError("Database SQLite bị lỗi")
    balances = {}
    for lot, received, expiry, moment, kind, quantity in connection.execute("""
        SELECT l.lot_id,l.received_on,l.expires_on,m.occurred_at,m.kind,m.quantity
        FROM lots l LEFT JOIN stock_movements m USING(lot_id)
        ORDER BY m.occurred_at,m.movement_id
    """):
        if (date.fromisoformat(received).isoformat() != received or
                date.fromisoformat(expiry).isoformat() != expiry or
                moment is None or datetime.fromisoformat(moment).isoformat(" ") != moment or
                not FIRST <= received <= moment[:10] <= LAST):
            raise ValueError(f"Mốc kho không hợp lệ tại lô {lot}")
        if lot not in balances and (kind != "receipt" or moment[:10] != received):
            raise ValueError(f"Thiếu dòng nhập đầu tiên tại lô {lot}")
        balances[lot] = balances.get(lot, 0) + (quantity if kind == "receipt" else -quantity)
        if balances[lot] < 0:
            raise ValueError(f"Tồn âm tại lô {lot}, lúc {moment}")
    return {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in TABLES}


def prepare(db, raw=ROOT / "data/raw"):
    db = Path(db)
    if not db.exists():
        db.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=db.parent) as folder:
            temporary = Path(folder) / "inventory.db"
            with connect(temporary, readonly=False) as connection:
                populate(connection)
                validate(connection)
            try:
                os.link(temporary, db)
            except FileExistsError:
                pass
    with connect(db) as connection:
        counts = validate(connection)
        raw.mkdir(parents=True, exist_ok=True)
        for table in TABLES:
            rows = connection.execute(f"SELECT * FROM {table} ORDER BY 1")
            with (raw / f"{table}.csv").open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(column[0] for column in rows.description)
                writer.writerows(rows)
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=DEFAULT_DB, type=Path)
    print(prepare(parser.parse_args().db))


if __name__ == "__main__":
    main()

