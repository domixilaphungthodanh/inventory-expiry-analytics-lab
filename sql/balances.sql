WITH totals AS (
    SELECT lot_id, SUM(CASE kind WHEN 'receipt' THEN quantity ELSE -quantity END) AS on_hand
    FROM stock_movements
    WHERE occurred_at < date(:as_of,'+1 day')
    GROUP BY lot_id
)
SELECT l.lot_id, l.product_id, p.name, p.unit, l.received_on, l.expires_on, t.on_hand
FROM totals t JOIN lots l USING(lot_id) JOIN products p USING(product_id)
ORDER BY l.lot_id
