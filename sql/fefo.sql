WITH balances AS ({balances}), ranked AS (
    SELECT lot_id,expires_on,received_on,on_hand,
           COALESCE(SUM(on_hand) OVER (
               ORDER BY expires_on,received_on,lot_id
               ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
           ),0) AS prior_stock
    FROM balances WHERE product_id=:product AND on_hand>0 AND expires_on>=:as_of
), allocation AS (
    SELECT lot_id,expires_on,received_on,on_hand,
           MAX(0,MIN(on_hand,:quantity-prior_stock)) AS allocated
    FROM ranked
)
SELECT * FROM allocation WHERE allocated>0 ORDER BY expires_on,received_on,lot_id
