import sqlite3
import pandas as pd

DATABASE = "books.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def save_products(df: pd.DataFrame):
    with get_connection() as conn:
        df.to_sql(
            "products",
            conn,
            if_exists="replace",
            index=False
        )


def get_all_products():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM products",
            conn
        )


def get_product_count():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM products"
        )

        return cursor.fetchone()[0]


def get_average_price():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT AVG(price) FROM products"
        )

        return cursor.fetchone()[0]


def get_book_by_id(book_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, price, url, availability
            FROM products
            WHERE id = ?
            """,
            (book_id,)
        )

        return cursor.fetchone()


def get_total_count():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM products"
        )

        return cursor.fetchone()[0]


def get_books_paginated(limit: int, offset: int):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, price, url, availability
            FROM products
            ORDER BY id
                LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )

        return cursor.fetchall()


def search_books(
        query: str,
        min_price: float | None = None,
        max_price: float | None = None,
        sort: str = "name"
):
    sql = """
          SELECT id, name, price, url, availability
          FROM products
          WHERE name LIKE ? \
          """

    params = [f"%{query}%"]

    if min_price is not None:
        sql += " AND price >= ?"
        params.append(min_price)

    if max_price is not None:
        sql += " AND price <= ?"
        params.append(max_price)

    if sort == "price_asc":
        sql += " ORDER BY price ASC"

    elif sort == "price_desc":
        sql += " ORDER BY price DESC"

    else:
        sql += " ORDER BY name ASC"

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(sql, params)

        return cursor.fetchall()


def get_stats():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*),
                AVG(price),
                MIN(price),
                MAX(price),
                SUM(price)
            FROM products
            """
        )

        return cursor.fetchone()