# Lời giải

## 1. Đếm mặt hàng

```sql
SELECT COUNT(*) FROM products;
```

## 2. Đếm lô

```sql
SELECT COUNT(*) FROM lots;
```

## 3. Đếm dòng nhập và xuất

```sql
SELECT kind,COUNT(*) FROM stock_movements GROUP BY kind;
```

## 4. Lọc mặt hàng có đơn vị hộp

```sql
SELECT * FROM products WHERE unit='hộp';
```

## 5. Lấy 10 lô nhập sớm nhất

```sql
SELECT * FROM lots ORDER BY received_on,lot_id LIMIT 10;
```

## 6. Lọc biến động vật lý đến hết 01/02

```sql
SELECT * FROM stock_movements WHERE occurred_at < date('2026-02-01','+1 day') ORDER BY occurred_at,movement_id;
```

## 7. Nối tên mặt hàng vào lô

```sql
SELECT l.lot_id,p.name,p.unit FROM lots l JOIN products p USING(product_id);
```

## 8. Đếm số lô theo mặt hàng

```sql
SELECT product_id,COUNT(*) FROM lots GROUP BY product_id;
```

## 9. Tính tồn theo lô

```sql
WITH ledger AS (SELECT lot_id,CASE kind WHEN 'receipt' THEN quantity ELSE -quantity END AS delta FROM stock_movements) SELECT lot_id,SUM(delta) AS on_hand FROM ledger GROUP BY lot_id;
```

## 10. Tìm lô hết tồn

```sql
SELECT * FROM (WITH ledger AS (SELECT lot_id,CASE kind WHEN 'receipt' THEN quantity ELSE -quantity END AS delta FROM stock_movements) SELECT lot_id,SUM(delta) AS on_hand FROM ledger GROUP BY lot_id) WHERE on_hand=0;
```

## 11. Tính số ngày còn hạn ngày 31/03

```sql
SELECT lot_id,julianday(expires_on)-julianday('2026-03-31') FROM lots;
```

## 12. Phân loại theo hạn

```sql
SELECT lot_id,expires_on,CASE WHEN expires_on<'2026-03-31' THEN 'expired' WHEN expires_on<=date('2026-03-31','+7 day') THEN 'expiring' ELSE 'valid' END AS status FROM lots;
```

## 13. Lọc lô hết hạn trước 01/04

```sql
SELECT * FROM lots WHERE expires_on<'2026-04-01';
```

## 14. Xếp thứ tự lô theo mặt hàng

```sql
SELECT lot_id,product_id,ROW_NUMBER() OVER(PARTITION BY product_id ORDER BY expires_on,received_on,lot_id) AS position FROM lots;
```

## 15. Tìm hai lô có cùng hạn trong một mặt hàng

```sql
SELECT product_id,expires_on,COUNT(*) FROM lots GROUP BY product_id,expires_on HAVING COUNT(*)>1;
```

## 16. Chia 12 hộp từ lô A và B

```sql
WITH lots(id,stock) AS (VALUES ('A',8),('B',10)), ranked AS (SELECT id, stock, COALESCE(SUM(stock) OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING),0) AS prior FROM lots) SELECT id,MAX(0,MIN(stock,12-prior)) AS allocated FROM ranked ORDER BY id;
```

## 17. Thử chia 21 hộp

```sql
WITH lots(id,stock) AS (VALUES ('A',8),('B',10)), ranked AS (SELECT id, stock, COALESCE(SUM(stock) OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING),0) AS prior FROM lots) SELECT id,MAX(0,MIN(stock,21-prior)) AS allocated FROM ranked ORDER BY id;
```

## 18. Tính số thiếu khi cần 21 hộp

```sql
SELECT 21-SUM(allocated) FROM (WITH lots(id,stock) AS (VALUES ('A',8),('B',10)), ranked AS (SELECT id, stock, COALESCE(SUM(stock) OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING),0) AS prior FROM lots) SELECT id,MAX(0,MIN(stock,21-prior)) AS allocated FROM ranked ORDER BY id);
```

## 19. Kiểm tra có mặt hàng chưa nhận lô vào ngày 01/01

```sql
SELECT p.product_id FROM products p WHERE NOT EXISTS(SELECT 1 FROM lots l WHERE l.product_id=p.product_id AND received_on<='2026-01-01');
```

## 20. Đếm số lần xuất theo ngày

```sql
SELECT date(occurred_at),COUNT(*) FROM stock_movements WHERE kind='issue' GROUP BY date(occurred_at);
```
