SELECT b.*,
       CASE WHEN on_hand=0 THEN 'empty'
            WHEN expires_on < :as_of THEN 'expired'
            WHEN expires_on <= date(:as_of,'+7 day') THEN 'expiring'
            ELSE 'valid' END AS status
FROM balances b
ORDER BY lot_id
