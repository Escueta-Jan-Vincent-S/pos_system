import sqlite3
import os
import sys
import math

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "database.db")

def get_connection():
    return sqlite3.connect(get_db_path())

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL DEFAULT 'staff',
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
        "classification TEXT DEFAULT ''",
        "product_barcode TEXT DEFAULT ''"
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
        CREATE TABLE IF NOT EXISTS demand_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL,
            item_name TEXT NOT NULL,
            qty INTEGER DEFAULT 0,
            log_date TEXT NOT NULL
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO accounts (email, role, is_current)
        VALUES ('admin@gmail.com', 'admin', 1)
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO accounts (email, role, is_current)
        VALUES ('staff@gmail.com', 'staff', 0)
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

def add_item(item_name, category, unit_cost, selling_price, current_stock, product_barcode=""):
    conn = get_connection()
    cursor = conn.cursor()
    barcode = get_next_barcode()
    cursor.execute("""
        INSERT INTO items (barcode, item_name, category, unit_cost, selling_price, current_stock, product_barcode)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (barcode, item_name, category, unit_cost, selling_price, current_stock, product_barcode))
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

def update_item(barcode, item_name, category, unit_cost, selling_price, current_stock, product_barcode=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE items
        SET item_name=?, category=?, unit_cost=?, selling_price=?, current_stock=?,
            product_barcode=COALESCE(?, product_barcode)
        WHERE barcode=?
    """, (item_name, category, unit_cost, selling_price, current_stock, product_barcode, barcode))
    conn.commit()
    conn.close()

def get_item_by_barcode(barcode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE barcode=? OR product_barcode=?", (barcode, barcode))
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
    """
    Compute ABC classification ONLY for items that have been computed
    (weekly_demand > 0). Items not yet computed are left untouched.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT barcode, weekly_demand FROM items
        WHERE weekly_demand > 0
        ORDER BY weekly_demand DESC
    """)
    items = cursor.fetchall()

    total = len(items)
    if total == 0:
        conn.close()
        return

    for idx, (barcode, demand) in enumerate(items):
        rank_pct = (idx + 1) / total
        if rank_pct <= 0.20:
            cls = "A"
        elif rank_pct <= 0.50:
            cls = "B"
        else:
            cls = "C"
        cursor.execute("UPDATE items SET classification=? WHERE barcode=?", (cls, barcode))

    # Clear classification for items not yet computed
    cursor.execute("UPDATE items SET classification='' WHERE weekly_demand = 0")
    conn.commit()
    conn.close()
def log_demand(cart):
    """Log sold quantities to demand_log table. Called after every payment."""
    from datetime import datetime
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    for item in cart:
        # Add to existing log entry for today, or insert new
        cursor.execute("""
            SELECT id, qty FROM demand_log
            WHERE barcode=? AND log_date=?
        """, (item["barcode"], today))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("UPDATE demand_log SET qty=? WHERE id=?",
                           (existing[1] + item["quantity"], existing[0]))
        else:
            cursor.execute("""
                INSERT INTO demand_log (barcode, item_name, qty, log_date)
                VALUES (?, ?, ?, ?)
            """, (item["barcode"], item["item_name"], item["quantity"], today))
    conn.commit()
    conn.close()


def get_demand_summary(timeframe):
    """
    Returns {barcode: total_qty} for the selected timeframe.
    Daily   = today only
    Weekly  = current week (Mon-Sun)
    Monthly = current month
    Annually= current year
    """
    from datetime import datetime, timedelta
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date()

    if timeframe == "Daily":
        date_filter = str(today)
        cursor.execute("""
            SELECT barcode, item_name, SUM(qty) FROM demand_log
            WHERE log_date = ?
            GROUP BY barcode
        """, (date_filter,))

    elif timeframe == "Weekly":
        # Monday of current week
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        cursor.execute("""
            SELECT barcode, item_name, SUM(qty) FROM demand_log
            WHERE log_date BETWEEN ? AND ?
            GROUP BY barcode
        """, (str(monday), str(sunday)))

    elif timeframe == "Monthly":
        month_start = today.replace(day=1)
        cursor.execute("""
            SELECT barcode, item_name, SUM(qty) FROM demand_log
            WHERE strftime('%Y-%m', log_date) = ?
            GROUP BY barcode
        """, (today.strftime("%Y-%m"),))

    elif timeframe == "Annually":
        cursor.execute("""
            SELECT barcode, item_name, SUM(qty) FROM demand_log
            WHERE strftime('%Y', log_date) = ?
            GROUP BY barcode
        """, (str(today.year),))

    rows = cursor.fetchall()
    conn.close()
    return {r[0]: {"item_name": r[1], "qty": r[2]} for r in rows}


def update_weekly_demand_from_timeframe(timeframe):
    """
    Update weekly_demand column for all items based on selected timeframe.
    For Weekly: use direct sum.
    For Daily: qty * 7 (projected weekly).
    For Monthly: qty / 4 (avg weekly).
    For Annually: qty / 52 (avg weekly).
    """
    summary = get_demand_summary(timeframe)
    if not summary:
        return 0  # no data

    conn = get_connection()
    cursor = conn.cursor()
    updated = 0

    for barcode, data in summary.items():
        qty = data["qty"]
        if timeframe == "Daily":
            weekly = round(qty * 7, 2)
        elif timeframe == "Weekly":
            weekly = round(qty, 2)
        elif timeframe == "Monthly":
            weekly = round(qty / 4, 2)
        elif timeframe == "Annually":
            weekly = round(qty / 52, 2)
        else:
            weekly = qty

        cursor.execute("UPDATE items SET weekly_demand=? WHERE barcode=?",
                       (weekly, barcode))
        updated += 1

    conn.commit()
    conn.close()
    return updated

def get_items_with_demand(start_date=None, end_date=None):
    """
    Returns items list with demand from demand_log for a date range.
    If no dates given, returns all-time cumulative demand.
    Columns: barcode, item_name, category, unit_cost, selling_price,
             current_stock, demand, classification, status
    """
    conn = get_connection()
    cursor = conn.cursor()
    if start_date and end_date:
        cursor.execute("""
            SELECT i.barcode, i.item_name, i.category, i.unit_cost, i.selling_price,
                   i.current_stock, COALESCE(SUM(d.qty), 0) as demand,
                   i.classification, i.status
            FROM items i
            LEFT JOIN demand_log d ON i.barcode = d.barcode
                AND d.log_date BETWEEN ? AND ?
            GROUP BY i.barcode
            ORDER BY i.barcode
        """, (start_date, end_date))
    else:
        cursor.execute("""
            SELECT i.barcode, i.item_name, i.category, i.unit_cost, i.selling_price,
                   i.current_stock, COALESCE(SUM(d.qty), 0) as demand,
                   i.classification, i.status
            FROM items i
            LEFT JOIN demand_log d ON i.barcode = d.barcode
            GROUP BY i.barcode
            ORDER BY i.barcode
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_classifications_by_demand_qty():
    """
    ABC classification based on CUMULATIVE demand quantity thresholds:
      A = demand > 200
      B = demand 91 to 200
      C = demand 90 and below (including 0)
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Get cumulative demand per item
    cursor.execute("""
        SELECT i.barcode, COALESCE(SUM(d.qty), 0) as total_demand
        FROM items i
        LEFT JOIN demand_log d ON i.barcode = d.barcode
        GROUP BY i.barcode
    """)
    rows = cursor.fetchall()
    for barcode, demand in rows:
        if demand > 200:
            cls = "A"
        elif demand >= 91:
            cls = "B"
        else:
            cls = "C"
        cursor.execute("UPDATE items SET classification=? WHERE barcode=?", (cls, barcode))
    conn.commit()
    conn.close()


def get_sales_and_profit_summary():
    """
    Returns a dict with total_sales and total_profit for:
    today, this_week, this_month, this_year
    Profit = (selling_price - unit_cost) * quantity per receipt item
    Only counts PAID receipts.
    Date stored as MM/DD/YY in receipts table.
    """
    from datetime import datetime, timedelta
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now()
    today_str  = today.strftime("%m/%d/%y")

    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start  = today.replace(month=1, day=1)

    def _query(start_str, end_str=None):
        # Convert MM/DD/YY dates to comparable format using SQLite
        if end_str:
            cursor.execute("""
                SELECT ri.selling_price, ri.quantity, i.unit_cost
                FROM receipt_items ri
                JOIN receipts r ON ri.receipt_no = r.receipt_no
                LEFT JOIN items i ON ri.barcode = i.barcode
                WHERE r.is_paid = 1
                AND strftime('%Y-%m-%d',
                    '20'||substr(r.date,7,2)||'-'||substr(r.date,1,2)||'-'||substr(r.date,4,2))
                BETWEEN ? AND ?
            """, (start_str, end_str))
        else:
            cursor.execute("""
                SELECT ri.selling_price, ri.quantity, i.unit_cost
                FROM receipt_items ri
                JOIN receipts r ON ri.receipt_no = r.receipt_no
                LEFT JOIN items i ON ri.barcode = i.barcode
                WHERE r.is_paid = 1
                AND strftime('%Y-%m-%d',
                    '20'||substr(r.date,7,2)||'-'||substr(r.date,1,2)||'-'||substr(r.date,4,2))
                = ?
            """, (start_str,))
        rows = cursor.fetchall()
        sales  = sum(sp * qty for sp, qty, _ in rows)
        profit = sum((sp - (uc or 0)) * qty for sp, qty, uc in rows)
        return round(sales, 2), round(profit, 2)

    result = {
        "today":      _query(today.strftime("%Y-%m-%d")),
        "this_week":  _query(week_start.strftime("%Y-%m-%d"),  today.strftime("%Y-%m-%d")),
        "this_month": _query(month_start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")),
        "this_year":  _query(year_start.strftime("%Y-%m-%d"),  today.strftime("%Y-%m-%d")),
    }
    conn.close()
    return result