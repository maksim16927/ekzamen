import os
import psycopg
from psycopg.rows import dict_row

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

DB_NAME = os.environ.get("TOYSTORE_DB", "toystore")
DB_USER = os.environ.get("TOYSTORE_USER")
DB_PASSWORD = os.environ.get("TOYSTORE_PASSWORD")
DB_HOST = os.environ.get("TOYSTORE_HOST")
DB_PORT = os.environ.get("TOYSTORE_PORT")


def connection_params(dbname):
    params = {"dbname": dbname, "autocommit": True, "row_factory": dict_row}
    if DB_USER:
        params["user"] = DB_USER
    if DB_PASSWORD:
        params["password"] = DB_PASSWORD
    if DB_HOST:
        params["host"] = DB_HOST
    if DB_PORT:
        params["port"] = DB_PORT
    return params


class Database:
    def __init__(self):
        self.ensure_database()
        self.connection = psycopg.connect(**connection_params(DB_NAME))
        if not self.schema_exists():
            self.create_schema()

    def ensure_database(self):
        try:
            test = psycopg.connect(**connection_params(DB_NAME))
            test.close()
            return
        except psycopg.OperationalError:
            pass
        service = psycopg.connect(**connection_params("postgres"))
        with service.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            if cur.fetchone() is None:
                cur.execute("CREATE DATABASE " + DB_NAME)
        service.close()

    def schema_exists(self):
        row = self.connection.execute("SELECT to_regclass('public.products') AS table_name").fetchone()
        return row["table_name"] is not None

    def create_schema(self):
        with open(SCHEMA_PATH, encoding="utf-8") as schema_file:
            script = schema_file.read()
        for statement in script.split(";"):
            command = statement.strip()
            if command:
                self.connection.execute(command)

    def authorize(self, login, password):
        query = (
            "SELECT u.user_id, u.full_name, r.role_name "
            "FROM users u "
            "JOIN roles r ON u.role_id = r.role_id "
            "WHERE u.login = %s AND u.password = %s"
        )
        return self.connection.execute(query, (login, password)).fetchone()

    def get_products(self, search_text="", category_id=None, sort_key=None):
        query = (
            "SELECT p.product_id, p.product_name, p.description, p.price, "
            "p.quantity, p.discount, p.image_path, "
            "c.category_name, m.manufacturer_name, s.supplier_name, u.unit_name "
            "FROM products p "
            "JOIN categories c ON p.category_id = c.category_id "
            "JOIN manufacturers m ON p.manufacturer_id = m.manufacturer_id "
            "JOIN suppliers s ON p.supplier_id = s.supplier_id "
            "JOIN units u ON p.unit_id = u.unit_id"
        )
        conditions = []
        params = []
        if search_text:
            pattern = "%" + search_text + "%"
            conditions.append(
                "(p.product_name ILIKE %s OR p.description ILIKE %s "
                "OR c.category_name ILIKE %s OR m.manufacturer_name ILIKE %s "
                "OR s.supplier_name ILIKE %s OR u.unit_name ILIKE %s)"
            )
            params.extend([pattern] * 6)
        if category_id:
            conditions.append("p.category_id = %s")
            params.append(category_id)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        sort_map = {
            "name_asc": " ORDER BY p.product_name ASC",
            "name_desc": " ORDER BY p.product_name DESC",
            "price_asc": " ORDER BY p.price ASC",
            "price_desc": " ORDER BY p.price DESC",
            "quantity_asc": " ORDER BY p.quantity ASC",
            "quantity_desc": " ORDER BY p.quantity DESC",
        }
        query += sort_map.get(sort_key, " ORDER BY p.product_id ASC")
        return self.connection.execute(query, params).fetchall()

    def get_product(self, product_id):
        query = "SELECT * FROM products WHERE product_id = %s"
        return self.connection.execute(query, (product_id,)).fetchone()

    def get_categories(self):
        return self.connection.execute(
            "SELECT category_id, category_name FROM categories ORDER BY category_name"
        ).fetchall()

    def get_manufacturers(self):
        return self.connection.execute(
            "SELECT manufacturer_id, manufacturer_name FROM manufacturers ORDER BY manufacturer_name"
        ).fetchall()

    def get_suppliers(self):
        return self.connection.execute(
            "SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name"
        ).fetchall()

    def get_units(self):
        return self.connection.execute(
            "SELECT unit_id, unit_name FROM units ORDER BY unit_name"
        ).fetchall()

    def get_next_product_id(self):
        row = self.connection.execute(
            "SELECT COALESCE(MAX(product_id), 0) + 1 AS next_id FROM products"
        ).fetchone()
        return row["next_id"]

    def add_product(self, data):
        new_id = self.get_next_product_id()
        query = (
            "INSERT INTO products "
            "(product_id, product_name, category_id, description, manufacturer_id, supplier_id, "
            "price, unit_id, quantity, discount, image_path) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            new_id, data["product_name"], data["category_id"], data["description"],
            data["manufacturer_id"], data["supplier_id"], data["price"],
            data["unit_id"], data["quantity"], data["discount"], data["image_path"],
        )
        self.connection.execute(query, params)
        return new_id

    def update_product(self, product_id, data):
        query = (
            "UPDATE products SET "
            "product_name = %s, category_id = %s, description = %s, manufacturer_id = %s, "
            "supplier_id = %s, price = %s, unit_id = %s, quantity = %s, discount = %s, image_path = %s "
            "WHERE product_id = %s"
        )
        params = (
            data["product_name"], data["category_id"], data["description"],
            data["manufacturer_id"], data["supplier_id"], data["price"],
            data["unit_id"], data["quantity"], data["discount"], data["image_path"],
            product_id,
        )
        self.connection.execute(query, params)

    def is_product_in_order(self, product_id):
        row = self.connection.execute(
            "SELECT COUNT(*) AS total FROM order_items WHERE product_id = %s", (product_id,)
        ).fetchone()
        return row["total"] > 0

    def delete_product(self, product_id):
        self.connection.execute("DELETE FROM products WHERE product_id = %s", (product_id,))

    def get_orders(self):
        query = (
            "SELECT o.order_id, o.order_date, u.full_name, "
            "COUNT(i.order_item_id) AS positions, "
            "COALESCE(SUM(i.quantity), 0) AS total_items "
            "FROM orders o "
            "JOIN users u ON o.user_id = u.user_id "
            "LEFT JOIN order_items i ON o.order_id = i.order_id "
            "GROUP BY o.order_id, o.order_date, u.full_name "
            "ORDER BY o.order_id"
        )
        return self.connection.execute(query).fetchall()
