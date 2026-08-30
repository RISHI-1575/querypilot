-- Sample sales database for QueryPilot.
-- Three small tables: customers, products, orders.

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    region  TEXT NOT NULL
);

CREATE TABLE products (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    category  TEXT NOT NULL,
    price     REAL NOT NULL
);

CREATE TABLE orders (
    id           INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL,
    product_id   INTEGER NOT NULL,
    quantity     INTEGER NOT NULL,
    order_date   TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- customers
INSERT INTO customers (id, name, region) VALUES
(1, 'Aarav Sharma',   'North'),
(2, 'Diya Patel',     'West'),
(3, 'Kabir Nair',     'South'),
(4, 'Meera Iyer',     'South'),
(5, 'Rohan Das',      'East'),
(6, 'Ananya Rao',     'West'),
(7, 'Vikram Singh',   'North'),
(8, 'Sara Khan',      'East');

-- products
INSERT INTO products (id, name, category, price) VALUES
(1, 'Wireless Mouse',   'Electronics', 799.0),
(2, 'Office Chair',     'Furniture',   4999.0),
(3, 'Coffee Mug',       'Kitchen',     299.0),
(4, 'Mechanical Keyboard', 'Electronics', 3499.0),
(5, 'Desk Lamp',        'Furniture',   1299.0),
(6, 'Water Bottle',     'Kitchen',     499.0);

-- orders
INSERT INTO orders (id, customer_id, product_id, quantity, order_date) VALUES
(1, 1, 1, 2, '2024-01-05'),
(2, 2, 4, 1, '2024-01-11'),
(3, 3, 2, 1, '2024-02-02'),
(4, 1, 3, 4, '2024-02-15'),
(5, 4, 5, 2, '2024-02-20'),
(6, 5, 1, 3, '2024-03-03'),
(7, 6, 6, 5, '2024-03-10'),
(8, 2, 2, 1, '2024-03-18'),
(9, 7, 4, 2, '2024-04-01'),
(10, 8, 3, 6, '2024-04-09'),
(11, 3, 1, 1, '2024-04-22'),
(12, 4, 4, 1, '2024-05-05'),
(13, 6, 2, 2, '2024-05-14'),
(14, 5, 5, 1, '2024-05-27'),
(15, 1, 6, 3, '2024-06-02'),
(16, 8, 1, 2, '2024-06-15'),
(17, 7, 3, 5, '2024-06-21'),
(18, 2, 5, 1, '2024-07-04'),
(19, 4, 2, 1, '2024-07-19'),
(20, 6, 4, 3, '2024-07-28');
