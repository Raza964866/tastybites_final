-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS tastybites_db;
USE tastybites_db;

-- Create tables
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(200) NOT NULL,
    password VARCHAR(200) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20) DEFAULT 'user',
    is_verified BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(6)
);

CREATE TABLE IF NOT EXISTS menu_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price FLOAT NOT NULL,
    category VARCHAR(50) NOT NULL,
    image VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS `order` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Pending',
    total_amount FLOAT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS order_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_item_id INT NOT NULL,
    quantity INT NOT NULL,
    price FLOAT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES `order`(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_item(id)
);

-- Insert admin user (password: admin123)
INSERT INTO user (name, email, phone, address, password, role)
VALUES ('Admin User', 'admin@tastybites.com', '1234567890', '123 Admin St', 
        '$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwxnG7JTTxqWxx/xxxxxxxxxxxx', 'admin');

-- Insert sample menu items
INSERT INTO menu_item (name, description, price, category, image)
VALUES 
    ('Classic Burger', 'Juicy beef patty with lettuce, tomato, and special sauce', 9.99, 'Burgers', 'burger.jpg'),
    ('Margherita Pizza', 'Traditional pizza with tomato sauce, mozzarella, and basil', 12.99, 'Pizza', 'pizza.jpg'),
    ('Caesar Salad', 'Crisp romaine lettuce with Caesar dressing, croutons, and parmesan', 7.99, 'Salads', 'salad.jpg'),
    ('Chocolate Brownie', 'Rich chocolate brownie with vanilla ice cream', 5.99, 'Desserts', 'brownie.jpg');