CREATE TABLE products(product_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, unit TEXT NOT NULL) STRICT;
CREATE TABLE lots(
    lot_id TEXT PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products,
    received_on TEXT NOT NULL, expires_on TEXT NOT NULL CHECK(expires_on >= received_on)
) STRICT;
CREATE TABLE stock_movements(
    movement_id INTEGER PRIMARY KEY, lot_id TEXT NOT NULL REFERENCES lots,
    occurred_at TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('receipt','issue')),
    quantity INTEGER NOT NULL CHECK(quantity > 0)
) STRICT;
CREATE UNIQUE INDEX one_receipt ON stock_movements(lot_id) WHERE kind='receipt';
CREATE INDEX lot_history ON stock_movements(lot_id,occurred_at,movement_id);
CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL) STRICT;

