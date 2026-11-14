from pathlib import Path
import tempfile
import unittest

from inventory_lab.analyze import export
from inventory_lab.db import ROOT, connect
from inventory_lab.metrics import checked_tables, verify_allocation
from inventory_lab.prepare_data import prepare, validate


class InventoryTests(unittest.TestCase):
    def test_demo_reproducible(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            db = root / "one.db"
            counts = prepare(db, root / "raw")
            self.assertEqual([counts[k] for k in ("products","lots","stock_movements")], [24,120,600])
            original = db.read_bytes()
            prepare(db, root / "raw")
            self.assertEqual(original, db.read_bytes())
            other = root / "two.db"
            prepare(other, root / "raw")
            with connect(db) as a, connect(other) as b:
                self.assertEqual(list(a.iterdump()), list(b.iterdump()))
                for day in ("2026-01-01","2026-02-15","2026-03-31"):
                    tables = checked_tables(a, day)
                    for product in range(1,25):
                        for quantity in (1,12,10000):
                            verify_allocation(a,tables["lots"],product,quantity,day)
                self.assertFalse(tables["expired"].empty)
                self.assertTrue(tables["lots"].status.eq("empty").any())
            self.assertEqual(original, db.read_bytes())

    def test_fefo_boundaries(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "fixture.db"
            with connect(db, readonly=False) as c, c:
                c.executescript((ROOT / "sql/schema.sql").read_text(encoding="utf-8"))
                c.execute("INSERT INTO products VALUES(1,'Test','hộp')")
                lots = [("A",1,"2026-01-02","2026-01-10",8),
                        ("B",1,"2026-01-02","2026-01-20",10),
                        ("C",1,"2026-01-20","2026-01-20",5),
                        ("D",1,"2026-01-20","2026-01-20",3)]
                c.executemany("INSERT INTO lots VALUES(?,?,?,?)", [row[:4] for row in lots])
                c.executemany("INSERT INTO stock_movements(lot_id,occurred_at,kind,quantity) VALUES(?,?,'receipt',?)",
                              [(lot, date+" 07:00:00", qty) for lot, _, date, _, qty in lots])
            with connect(db) as c:
                for day, quantity, expected, missing in [
                    ("2026-01-10",8,[("A",8)],0),
                    ("2026-01-10",12,[("A",8),("B",4)],0),
                    ("2026-01-11",12,[("B",10)],2),
                    ("2026-01-20",16,[("B",10),("C",5),("D",1)],0),
                    ("2026-01-21",1,[],1),
                ]:
                    tables = checked_tables(c, day)
                    result, shortage = verify_allocation(c,tables["lots"],1,quantity,day)
                    self.assertEqual((list(zip(result.lot_id, result.allocated)),shortage),(expected,missing))
                self.assertEqual(checked_tables(c,"2026-01-02")["expiring"].lot_id.tolist(),[])
                self.assertEqual(checked_tables(c,"2026-01-03")["expiring"].lot_id.tolist(),["A"])
                with self.assertRaises(ValueError):
                    verify_allocation(c,tables["lots"],1,0,"2026-01-20")
            out = Path(folder)/"empty"
            export(db,out,"2026-01-01")
            self.assertEqual((len(list(out.glob("*.csv"))),len(list(out.glob("*.png")))), (6,4))
            self.assertTrue((out/"report.md").exists())
            with connect(db, readonly=False) as c, c:
                c.execute("INSERT INTO stock_movements VALUES(100,'A','2026-01-06 09:00:00','issue',9)")
                with self.assertRaisesRegex(ValueError, "Tồn âm"):
                    validate(c)

