from contextlib import contextmanager
from datetime import date
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "database/inventory.db"
FIRST = "2026-01-01"
LAST = "2026-03-31"
TABLES = ("products", "lots", "stock_movements", "metadata")


def observation(value):
    if date.fromisoformat(value).isoformat() != value or not FIRST <= value <= LAST:
        raise ValueError("Nhập ngày YYYY-MM-DD trong quý I/2026")
    return value


@contextmanager
def connect(path=DEFAULT_DB, *, readonly=True):
    path = Path(path).resolve()
    connection = sqlite3.connect(path.as_uri() + "?mode=ro" if readonly else path, uri=readonly)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.row_factory = sqlite3.Row
        yield connection
    finally:
        connection.close()

