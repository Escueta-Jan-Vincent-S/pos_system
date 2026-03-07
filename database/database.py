import sqlite3
import os
import sys
import math

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "pos.db")

def get_connection():
    return sqlite3.connect(get_db_path())

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL DEFAULT 'student',
            is_current INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL UNIQUE,
            item_name TEXT NOT NULL,
            category TEXT,
            unit_cost REAL DEFAULT 0,
            selling_price REAL DEFAULT 0,
            current_stock INTEGER DEFAULT 0,
            weekly_demand REAL DEFAULT 0,
            safety_stock REAL DEFAULT 0,
            rop REAL DEFAULT 0,
            min_level REAL DEFAULT 0,
            max_level REAL DEFAULT 0,
            status TEXT DEFAULT '',
            classification TEXT DEFAULT ''
        )
    """)

    # Migrate existing items table if columns missing
    for col in [
        "weekly_demand REAL DEFAULT 0",
        "safety_stock REAL DEFAULT 0",
        "rop REAL DEFAULT 0",
        "min_level REAL DEFAULT 0",
        "max_level REAL DEFAULT 0",
        "status TEXT DEFAULT ''",
        "classification TEXT DEFAULT ''"
    ]:
        try:
            cursor.execute(f"ALTER TABLE items ADD COLUMN {col}")
        except:
            pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_no TEXT NOT NULL UNIQUE,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            total REAL DEFAULT 0,
            cash REAL DEFAULT 0,
            change_amount REAL DEFAULT 0,
            is_paid INTEGER DEFAULT 1
        )
    """)

    # Migrate existing receipts table if is_paid column missing
    try:
        cursor.execute("ALTER TABLE receipts ADD COLUMN is_paid INTEGER DEFAULT 1")
    except:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipt_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_no TEXT NOT NULL,
            barcode TEXT,
            item_name TEXT,
            selling_price REAL DEFAULT 0,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (receipt_no) REFERENCES receipts(receipt_no)
        )
    """)

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
    cursor.execute("""
        SELECT barcode, item_name, category, unit_cost, selling_price,
               current_stock, weekly_demand, classification, status
        FROM items
    """)
    items = cursor.fetchall()
    conn.close()
    return items

def get_all_items_with_reorder():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT barcode, item_name, category, min_level, max_level, status
        FROM items
    """)
    items = cursor.fetchall()
    conn.close()
    return items

def delete_item(barcode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE barcode = ?", (barcode,))
    conn.commit()
    conn.close()

def update_item(barcode, item_name, category, unit_cost, selling_price, current_stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE items
        SET item_name=?, category=?, unit_cost=?, selling_price=?, current_stock=?
        WHERE barcode=?
    """, (item_name, category, unit_cost, selling_price, current_stock, barcode))
    conn.commit()
    conn.close()

def get_item_by_barcode(barcode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE barcode=?", (barcode,))
    item = cursor.fetchone()
    conn.close()
    return item

def update_reorder_info(barcode, safety_stock, rop, min_level, max_level, status, weekly_demand):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE items
        SET safety_stock=?, rop=?, min_level=?, max_level=?, status=?, weekly_demand=?
        WHERE barcode=?
    """, (safety_stock, rop, min_level, max_level, status, weekly_demand, barcode))
    conn.commit()
    conn.close()

def save_receipt(cart, total, cash, change_amount, is_paid=1, receipt_no=None):
    import random
    from datetime import datetime
    conn = get_connection()
    cursor = conn.cursor()
    if not receipt_no:
        receipt_no = f"REC{random.randint(10000, 99999)}"
    now = datetime.now()
    date_str = now.strftime("%m/%d/%y")
    time_str = now.strftime("%H:%M")
    cursor.execute("""
        INSERT OR IGNORE INTO receipts (receipt_no, date, time, total, cash, change_amount, is_paid)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (receipt_no, date_str, time_str, total, cash, change_amount, is_paid))
    # Only insert items if this is a new receipt
    cursor.execute("SELECT COUNT(*) FROM receipt_items WHERE receipt_no = ?", (receipt_no,))
    if cursor.fetchone()[0] == 0:
        for item in cart:
            cursor.execute("""
                INSERT INTO receipt_items (receipt_no, barcode, item_name, selling_price, quantity)
                VALUES (?, ?, ?, ?, ?)
            """, (receipt_no, item["barcode"], item["item_name"], item["selling_price"], item["quantity"]))
    conn.commit()
    conn.close()
    return receipt_no


def mark_receipt_paid(receipt_no, cash, change_amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE receipts SET is_paid=1, cash=?, change_amount=? WHERE receipt_no=?
    """, (cash, change_amount, receipt_no))
    conn.commit()
    conn.close()

def get_all_receipts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date, time, receipt_no, total, is_paid FROM receipts ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def toggle_receipt_paid(receipt_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE receipts SET is_paid = CASE WHEN is_paid = 1 THEN 0 ELSE 1 END WHERE receipt_no = ?", (receipt_no,))
    conn.commit()
    conn.close()


def delete_receipt(receipt_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM receipt_items WHERE receipt_no = ?", (receipt_no,))
    cursor.execute("DELETE FROM receipts WHERE receipt_no = ?", (receipt_no,))
    conn.commit()
    conn.close()

def get_receipt_by_no(receipt_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT barcode, item_name, selling_price, quantity
        FROM receipt_items WHERE receipt_no = ?
    """, (receipt_no,))
    rows = cursor.fetchall()
    conn.close()
    return [{"barcode": r[0], "item_name": r[1], "selling_price": r[2], "quantity": r[3]} for r in rows]

def update_all_classifications():
    """Compute ABC classification for all items based on weekly demand."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT barcode, weekly_demand FROM items ORDER BY weekly_demand DESC")
    items = cursor.fetchall()
    conn.close()

    total = len(items)
    if total == 0:
        return

    for idx, (barcode, demand) in enumerate(items):
        rank_pct = (idx + 1) / total
        if rank_pct <= 0.20:
            cls = "A"
        elif rank_pct <= 0.50:
            cls = "B"
        else:
            cls = "C"

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE items SET classification=? WHERE barcode=?", (cls, barcode))
        conn.commit()
        conn.close()