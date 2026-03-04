import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "pos.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL DEFAULT 'student',
            is_current INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL UNIQUE,
            item_name TEXT NOT NULL,
            category TEXT,
            unit_cost REAL DEFAULT 0,
            selling_price REAL DEFAULT 0,
            current_stock INTEGER DEFAULT 0
        )
    """)

    # Seed default admin
    cursor.execute("""
        INSERT OR IGNORE INTO accounts (email, role, is_current)
        VALUES ('admin@gmail.com', 'admin', 1)
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO accounts (email, role, is_current)
        VALUES ('student@gmail.com', 'student', 0)
    """)

    conn.commit()
    conn.close()

def get_all_accounts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, role, is_current FROM accounts")
    accounts = cursor.fetchall()
    conn.close()
    return accounts

def switch_account(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET is_current = 0")
    cursor.execute("UPDATE accounts SET is_current = 1 WHERE id = ?", (account_id,))
    conn.commit()
    conn.close()

def get_next_barcode():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(CAST(barcode AS INTEGER)) FROM items")
    result = cursor.fetchone()[0]
    conn.close()
    return str((result or 1000) + 1)

def add_item(item_name, category, unit_cost, selling_price, current_stock):
    conn = get_connection()
    cursor = conn.cursor()
    barcode = get_next_barcode()
    cursor.execute("""
        INSERT INTO items (barcode, item_name, category, unit_cost, selling_price, current_stock)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (barcode, item_name, category, unit_cost, selling_price, current_stock))
    conn.commit()
    conn.close()

def get_all_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT barcode, item_name, category, unit_cost, selling_price, current_stock FROM items")
    items = cursor.fetchall()
    conn.close()
    return items

def delete_item(barcode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE barcode = ?", (barcode,))
    conn.commit()
    conn.close()