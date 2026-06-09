CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles (role_id)
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE manufacturers (
    manufacturer_id SERIAL PRIMARY KEY,
    manufacturer_name TEXT NOT NULL UNIQUE
);

CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name TEXT NOT NULL UNIQUE
);

CREATE TABLE units (
    unit_id SERIAL PRIMARY KEY,
    unit_name TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories (category_id),
    description TEXT,
    manufacturer_id INTEGER NOT NULL REFERENCES manufacturers (manufacturer_id),
    supplier_id INTEGER NOT NULL REFERENCES suppliers (supplier_id),
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    unit_id INTEGER NOT NULL REFERENCES units (unit_id),
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    discount NUMERIC(5, 2) NOT NULL DEFAULT 0 CHECK (discount >= 0 AND discount <= 100),
    image_path TEXT
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (user_id),
    order_date DATE NOT NULL
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders (order_id),
    product_id INTEGER NOT NULL REFERENCES products (product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0)
);

INSERT INTO roles (role_name) VALUES
    ('Администратор'),
    ('Менеджер'),
    ('Клиент');

INSERT INTO users (login, password, full_name, role_id) VALUES
    ('admin', 'admin123', 'Иванов Иван Иванович', 1),
    ('manager', 'manager123', 'Петров Пётр Петрович', 2),
    ('client', 'client123', 'Сидорова Анна Сергеевна', 3);

INSERT INTO categories (category_name) VALUES
    ('Конструкторы'),
    ('Мягкие игрушки'),
    ('Машинки'),
    ('Куклы'),
    ('Настольные игры');

INSERT INTO manufacturers (manufacturer_name) VALUES
    ('LEGO'),
    ('Hasbro'),
    ('Mattel'),
    ('Зеленоград-Тойз'),
    ('Bandai');

INSERT INTO suppliers (supplier_name) VALUES
    ('ООО Игрушка-Опт'),
    ('ИП Смирнов'),
    ('ТД Детство'),
    ('Toys Import');

INSERT INTO units (unit_name) VALUES
    ('шт'),
    ('упак'),
    ('набор');

INSERT INTO products (product_name, category_id, description, manufacturer_id, supplier_id, price, unit_id, quantity, discount, image_path) VALUES
    ('Конструктор LEGO City Полицейский участок', 1, 'Большой игровой набор с фигурками и машинами', 1, 1, 4999.99, 3, 15, 20, NULL),
    ('Плюшевый медведь Тёдди', 2, 'Мягкая игрушка из гипоаллергенного материала', 4, 3, 1299.50, 1, 0, 0, NULL),
    ('Радиоуправляемая машинка Дрифт', 3, 'Гоночная машина на пульте управления, масштаб 1:18', 2, 2, 2500.00, 1, 7, 10, NULL),
    ('Кукла Барби Модница', 4, 'Кукла с набором аксессуаров и одежды', 3, 1, 1899.00, 1, 30, 0, NULL),
    ('Настольная игра Монополия', 5, 'Классическая экономическая стратегия для всей семьи', 2, 3, 2199.00, 3, 5, 18, NULL),
    ('Конструктор Технолог Ферма', 1, 'Развивающий конструктор для детей от 3 лет', 4, 2, 999.00, 3, 0, 0, NULL),
    ('Робот-трансформер Оптимус', 3, 'Трансформируется из робота в грузовик', 5, 4, 3499.90, 1, 12, 25, NULL),
    ('Пазл Карта мира 1000 деталей', 5, 'Большой пазл с изображением политической карты мира', 2, 3, 599.99, 2, 50, 5, NULL);

INSERT INTO orders (user_id, order_date) VALUES
    (3, '2026-05-20');

INSERT INTO order_items (order_id, product_id, quantity) VALUES
    (1, 1, 2);
