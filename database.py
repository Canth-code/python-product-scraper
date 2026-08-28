import sqlite3
import pandas as pd


DATABASE = "books.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def save_products(df):
    conn = get_connection()

    df.to_sql(
        "products",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()


def get_all_products():
    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM products",
        conn
    )

    conn.close()

    return df


def get_product_count():
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM products"
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


def get_average_price():
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT AVG(price) FROM products"
    )

    average = cursor.fetchone()[0]

    conn.close()

    return average


def get_products_paginated(limit, offset):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT rowid, name, price, url, availability
        FROM products
        ORDER BY rowid
            LIMIT ? OFFSET ?
        """,
        (limit, offset)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_product_by_id(product_id):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT rowid, name, price, url, availability
        FROM products
        WHERE rowid = ?
        """,
        (product_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def search_products(
        query_text="",
        min_price=None,
        max_price=None,
        sort="name",
        limit=20,
        offset=0
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
            SELECT rowid, name, price, url, availability
            FROM products
            WHERE name LIKE ? \
            """

    params = [f"%{query_text}%"]

    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)

    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)

    if sort == "price_asc":
        query += " ORDER BY price ASC"

    elif sort == "price_desc":
        query += " ORDER BY price DESC"

    else:
        query += " ORDER BY name ASC"

    query += " LIMIT ? OFFSET ?"

    params.extend([limit, offset])

    cursor.execute(query, params)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_stats():
    conn = get_connection()

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

    row = cursor.fetchone()

    conn.close()

    return row
def get_search_count(
        query_text="",
        min_price=None,
        max_price=None
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
            SELECT COUNT(*)
            FROM products
            WHERE name LIKE ? \
            """

    params = [f"%{query_text}%"]

    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)

    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)

    cursor.execute(query, params)

    count = cursor.fetchone()[0]

    conn.close()

    return count