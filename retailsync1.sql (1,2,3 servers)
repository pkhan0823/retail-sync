

-- =====================================================
-- COMPLETE POSTGRESQL SCRIPT
-- Tables + 5,000 Records + Indexes + Performance
-- EXPLAIN ANALYZE + Slow Queries + Deadlock Demo
-- =====================================================


-- 1. DROP TABLES
DROP TABLE IF EXISTS billing CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;


-- 2. CREATE TABLES

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL
        CHECK(total_amount >= 0),
    status VARCHAR(15) DEFAULT 'pending',

    CONSTRAINT chk_order_status
        CHECK(status IN (
            'pending', 'shipped', 'delivered',
            'cancelled', 'done'
        ))
);


CREATE TABLE inventory (
    product_id SERIAL PRIMARY KEY,
    quantity INT NOT NULL CHECK(quantity >= 0),
    restock_date DATE DEFAULT CURRENT_DATE,
    location VARCHAR(20) NOT NULL
);


CREATE TABLE billing (
    bill_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    amount NUMERIC(10,2) NOT NULL CHECK(amount >= 0),
    bill_status VARCHAR(15) DEFAULT 'unpaid',
    bill_date DATE DEFAULT CURRENT_DATE,

    CONSTRAINT fk_billing_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_billing_status
        CHECK(bill_status IN ('paid', 'unpaid', 'pending'))
);


-- 3. INSERT ORIGINAL 20 ORDERS

INSERT INTO orders(customer_id, order_date, total_amount, status)
VALUES
(101, '2026-05-23', 399.00, 'done'),
(102, '2026-05-29', 564.50, 'shipped'),
(103, '2026-06-02', 500.00, 'delivered'),
(104, '2026-06-05', 7500.00, 'pending'),
(105, '2026-06-12', 5320.00, 'pending'),
(106, '2026-06-12', 52000.00, 'cancelled'),
(107, '2026-06-18', 5320.20, 'delivered'),
(108, '2026-06-20', 300.00, 'delivered'),
(109, '2026-06-20', 7500.00, 'pending'),
(110, '2026-06-21', 7100.00, 'delivered'),
(111, '2026-07-25', 8200.00, 'delivered'),
(112, '2026-07-26', 1250.00, 'pending'),
(113, '2026-07-28', 999.00, 'shipped'),
(114, '2026-08-01', 4300.00, 'delivered'),
(115, '2026-08-03', 15000.00, 'cancelled'),
(116, '2026-08-05', 620.00, 'delivered'),
(117, '2026-08-07', 2100.00, 'pending'),
(118, '2026-08-10', 890.00, 'shipped'),
(119, '2026-08-12', 3300.00, 'delivered'),
(120, '2026-08-15', 450.00, 'done');


-- 4. INSERT ORIGINAL 20 BILLING RECORDS

INSERT INTO billing(order_id, amount, bill_status, bill_date)
VALUES
(1, 399.00, 'paid', DEFAULT),
(2, 564.50, 'paid', DEFAULT),
(3, 500.00, 'paid', DEFAULT),
(4, 7500.00, 'unpaid', DEFAULT),
(5, 5320.00, 'pending', DEFAULT),
(6, 52000.00, 'unpaid', DEFAULT),
(7, 5320.20, 'paid', DEFAULT),
(8, 300.00, 'paid', DEFAULT),
(9, 7500.00, 'pending', DEFAULT),
(10, 7100.00, 'paid', DEFAULT),
(11, 8200.00, 'paid', DEFAULT),
(12, 1250.00, 'pending', DEFAULT),
(13, 999.00, 'unpaid', DEFAULT),
(14, 4300.00, 'paid', DEFAULT),
(15, 15000.00, 'unpaid', DEFAULT),
(16, 620.00, 'paid', DEFAULT),
(17, 2100.00, 'pending', DEFAULT),
(18, 890.00, 'unpaid', DEFAULT),
(19, 3300.00, 'paid', DEFAULT),
(20, 450.00, 'paid', DEFAULT);


-- 5. INSERT ORIGINAL 20 INVENTORY RECORDS

INSERT INTO inventory(quantity, restock_date, location)
VALUES
(60, DEFAULT, 'Store 1'),
(20, DEFAULT, 'Store 2'),
(85, DEFAULT, 'Store 1'),
(10, DEFAULT, 'Store 5'),
(20, DEFAULT, 'Store 2'),
(35, DEFAULT, 'Store 2'),
(20, DEFAULT, 'Store 2'),
(45, '2026-07-01', 'Store 3'),
(12, '2026-07-05', 'Store 4'),
(90, DEFAULT, 'Store 1'),
(5, '2026-08-01', 'Store 2'),
(30, DEFAULT, 'Store 5'),
(75, DEFAULT, 'Store 3'),
(18, '2026-08-10', 'Store 4'),
(60, DEFAULT, 'Store 1'),
(22, DEFAULT, 'Store 2'),
(0, '2026-09-01', 'Store 3'),
(40, DEFAULT, 'Store 5'),
(15, DEFAULT, 'Store 4'),
(50, '2026-09-10', 'Store 1');


-- 6. INSERT 5,000 ADDITIONAL ORDERS

INSERT INTO orders(customer_id, order_date, total_amount, status)
SELECT
    120 + gs,
    DATE '2026-01-01' + (gs % 300)::INT,
    ROUND((100 + random() * 10000)::NUMERIC, 2),
    (ARRAY[
        'pending', 'shipped', 'delivered',
        'cancelled', 'done'
    ])[1 + floor(random() * 5)::INT]
FROM generate_series(1, 5000) AS gs;


-- 7. INSERT BILLING FOR THE NEW ORDERS

INSERT INTO billing(order_id, amount, bill_status, bill_date)
SELECT
    order_id,
    total_amount,
    (ARRAY['paid', 'unpaid', 'pending'])
        [1 + floor(random() * 3)::INT],
    CURRENT_DATE - floor(random() * 100)::INT
FROM orders
WHERE order_id > 20;


-- 8. INSERT 5,000 ADDITIONAL INVENTORY RECORDS

INSERT INTO inventory(quantity, restock_date, location)
SELECT
    floor(random() * 101)::INT,
    CURRENT_DATE - floor(random() * 100)::INT,
    'Store ' || (1 + floor(random() * 5)::INT)
FROM generate_series(1, 5000);


-- 9. CREATE INDEXES

CREATE INDEX idx_billing_status
ON billing(bill_status);

CREATE INDEX idx_orders_status
ON orders(status);

CREATE INDEX idx_inventory_quantity
ON inventory(quantity);


-- 10. UPDATE STATISTICS

ANALYZE orders;
ANALYZE billing;
ANALYZE inventory;


-- 11. DISPLAY COMPLETE TABLE DATA

SELECT * FROM orders ORDER BY order_id;
SELECT * FROM billing ORDER BY bill_id;
SELECT * FROM inventory ORDER BY product_id;


-- 12. VERIFY TOTAL RECORDS

SELECT 'orders' AS table_name, COUNT(*) AS total_records
FROM orders
UNION ALL
SELECT 'billing', COUNT(*) FROM billing
UNION ALL
SELECT 'inventory', COUNT(*) FROM inventory;


-- 13. INSPECT TABLE CONSTRAINTS

SELECT
    conname,
    conrelid::regclass AS table_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid IN (
    'orders'::regclass,
    'billing'::regclass,
    'inventory'::regclass
);


-- 14. TEST UPDATE

UPDATE orders
SET total_amount = 6000
WHERE customer_id = 101;


-- 15. JOIN QUERY

SELECT
    b.bill_id,
    b.order_id,
    b.bill_status,
    b.amount,
    o.customer_id,
    o.total_amount,
    o.status
FROM billing b
JOIN orders o
    ON b.order_id = o.order_id
WHERE b.bill_status = 'unpaid';


-- 16. EXPLAIN ANALYZE

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    b.bill_id,
    b.order_id,
    b.bill_status,
    b.amount,
    o.customer_id,
    o.total_amount,
    o.status
FROM billing b
JOIN orders o
    ON b.order_id = o.order_id
WHERE b.bill_status = 'unpaid';


-- 17. INVENTORY PERFORMANCE ANALYSIS

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM inventory
WHERE quantity < 20;


-- 18. ORDERS PERFORMANCE ANALYSIS

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE status = 'pending';


-- 19. CURRENT SLOW QUERY MONITORING
-- Shows active queries running longer than 2 seconds.

SELECT
    pid,
    usename,
    state,
    NOW() - query_start AS duration,
    query
FROM pg_stat_activity
WHERE state = 'active'
  AND query_start IS NOT NULL
  AND NOW() - query_start > INTERVAL '2 seconds'
ORDER BY duration DESC;


-- 20. DEADLOCK STATISTICS

SELECT
    datname,
    deadlocks,
    stats_reset
FROM pg_stat_database
WHERE datname = current_database();


-- 21. CONNECTION MONITORING

SELECT
    state,
    COUNT(*) AS connection_count
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state
ORDER BY state;


-- 22. FINAL RECORD COUNTS

SELECT
    (SELECT COUNT(*) FROM orders) AS total_orders,
    (SELECT COUNT(*) FROM billing) AS total_billing,
    (SELECT COUNT(*) FROM inventory) AS total_inventory;


-- =====================================================
-- DEADLOCK DEMONSTRATION
-- =====================================================
-- IMPORTANT:
-- Do NOT execute this section as one normal script.
-- Use two separate PostgreSQL query sessions.
--
-- SESSION 1:
--
-- BEGIN;
-- UPDATE orders
-- SET total_amount = total_amount + 100
-- WHERE order_id = 1;
--
-- SESSION 2:
--
-- BEGIN;
-- UPDATE billing
-- SET amount = amount + 100
-- WHERE bill_id = 1;
--
-- SESSION 1 (will wait):
--
-- UPDATE billing
-- SET amount = amount + 50
-- WHERE bill_id = 1;
--
-- SESSION 2 (creates the deadlock):
--
-- UPDATE orders
-- SET total_amount = total_amount + 50
-- WHERE order_id = 1;
--
-- PostgreSQL detects the deadlock and aborts one transaction.
--
-- After the test, run ROLLBACK in the session
-- whose transaction is still open.
--
-- =====================================================
-- END OF SCRIPT
-- =====================================================
