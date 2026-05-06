
import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "store.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # ─── الأصناف ───────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT    UNIQUE NOT NULL,
            name        TEXT    NOT NULL,
            category    TEXT    DEFAULT '',
            description TEXT    DEFAULT '',
            unit        TEXT    DEFAULT 'قطعة',
            cost_price  REAL    DEFAULT 0,
            sell_price  REAL    DEFAULT 0,
            min_stock   INTEGER DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # ─── التوريد ───────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS supplies (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  INTEGER NOT NULL REFERENCES products(id),
            quantity    INTEGER NOT NULL,
            cost_price  REAL    DEFAULT 0,
            supplier    TEXT    DEFAULT '',
            notes       TEXT    DEFAULT '',
            supply_date TEXT    DEFAULT (date('now','localtime')),
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # ─── المبيعات ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  INTEGER REFERENCES products(id),
            quantity    INTEGER NOT NULL,
            unit_price  REAL    NOT NULL,
            total       REAL    NOT NULL,
            discount    REAL    DEFAULT 0,
            notes       TEXT    DEFAULT '',
            sale_date   TEXT    DEFAULT (date('now','localtime')),
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # ─── المصروفات ─────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            category     TEXT    DEFAULT 'عام',
            description  TEXT    NOT NULL,
            amount       REAL    NOT NULL,
            expense_date TEXT    DEFAULT (date('now','localtime')),
            created_at   TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # ─── الديون ────────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS debts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            debtor_name  TEXT    NOT NULL,
            amount       REAL    NOT NULL,
            paid         REAL    DEFAULT 0,
            description  TEXT    DEFAULT '',
            debt_date    TEXT    DEFAULT (date('now','localtime')),
            due_date     TEXT    DEFAULT '',
            status       TEXT    DEFAULT 'مفتوح',
            created_at   TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # ─── سداد الديون ───────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS debt_payments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            debt_id    INTEGER NOT NULL REFERENCES debts(id),
            amount     REAL    NOT NULL,
            pay_date   TEXT    DEFAULT (date('now','localtime')),
            notes      TEXT    DEFAULT '',
            created_at TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # ─── الجرد ─────────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory_sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    DEFAULT '',
            start_date  TEXT    NOT NULL,
            end_date    TEXT    NOT NULL,
            notes       TEXT    DEFAULT '',
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id   INTEGER NOT NULL REFERENCES inventory_sessions(id),
            product_id   INTEGER NOT NULL REFERENCES products(id),
            actual_count INTEGER DEFAULT 0,
            notes        TEXT    DEFAULT '',
            created_at   TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    conn.commit()
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════════
#  PRODUCTS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_product_code(category=""):
    """توليد كود فريد للمنتج بصيغة بسيطة (P-0001)"""
    conn = get_conn()
    c = conn.cursor()
    # الحصول على أعلى ID حالي لضمان تسلسل الكود
    c.execute("SELECT MAX(id) FROM products")
    last_id = c.fetchone()[0] or 0
    conn.close()
    return f"P-{(last_id + 1):04d}"

def add_product(name, category="", description="", unit="قطعة",
                cost_price=0, sell_price=0, min_stock=0):
    code = generate_product_code(category)
    conn = get_conn()
    conn.execute("""
        INSERT INTO products (code,name,category,description,unit,cost_price,sell_price,min_stock)
        VALUES (?,?,?,?,?,?,?,?)
    """, (code, name, category, description, unit, cost_price, sell_price, min_stock))
    conn.commit()
    conn.close()
    return code

def update_product(pid, name, category, description, unit, cost_price, sell_price, min_stock):
    conn = get_conn()
    conn.execute("""
        UPDATE products SET name=?,category=?,description=?,unit=?,
        cost_price=?,sell_price=?,min_stock=? WHERE id=?
    """, (name, category, description, unit, cost_price, sell_price, min_stock, pid))
    conn.commit()
    conn.close()

def delete_product(pid):
    conn = get_conn()
    try:
        # حذف السجلات المرتبطة أولاً لتجنب قيود المفتاح الأجنبي
        conn.execute("DELETE FROM sales WHERE product_id=?", (pid,))
        conn.execute("DELETE FROM supplies WHERE product_id=?", (pid,))
        conn.execute("DELETE FROM inventory_items WHERE product_id=?", (pid,))
        # ثم حذف الصنف نفسه
        conn.execute("DELETE FROM products WHERE id=?", (pid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_all_products():
    conn = get_conn()
    # إخفاء صنف "المبيعات العامة" أو أي أصناف نظام إن وجدت
    rows = conn.execute("SELECT * FROM products WHERE code != 'GENERAL' ORDER BY name").fetchall()
    conn.close()
    return rows

def get_product(pid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    conn.close()
    return row

def get_general_product_id():
    return None

def get_product_stock(pid):
    """حساب المخزون الحالي = توريد - مبيعات"""
    conn = get_conn()
    sup = conn.execute("SELECT COALESCE(SUM(quantity),0) FROM supplies WHERE product_id=?", (pid,)).fetchone()[0]
    sal = conn.execute("SELECT COALESCE(SUM(quantity),0) FROM sales WHERE product_id=?", (pid,)).fetchone()[0]
    conn.close()
    return sup - sal

# ═══════════════════════════════════════════════════════════════════════════════
#  SUPPLIES
# ═══════════════════════════════════════════════════════════════════════════════

def add_supply(product_id, quantity, cost_price=0, supplier="", notes="", supply_date=None):
    if supply_date is None:
        supply_date = date.today().isoformat()
    conn = get_conn()
    conn.execute("""
        INSERT INTO supplies (product_id,quantity,cost_price,supplier,notes,supply_date)
        VALUES (?,?,?,?,?,?)
    """, (product_id, quantity, cost_price, supplier, notes, supply_date))
    conn.commit()
    conn.close()

def get_supplies(product_id=None, from_date=None, to_date=None):
    conn = get_conn()
    q = """
        SELECT s.*, p.name as product_name, p.code as product_code, p.sell_price
        FROM supplies s JOIN products p ON s.product_id=p.id
        WHERE 1=1
    """
    params = []
    if product_id:
        q += " AND s.product_id=?"; params.append(product_id)
    if from_date:
        q += " AND s.supply_date>=?"; params.append(from_date)
    if to_date:
        q += " AND s.supply_date<=?"; params.append(to_date)
    q += " ORDER BY s.supply_date DESC, s.id DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return rows

def delete_supply(sid):
    conn = get_conn()
    conn.execute("DELETE FROM supplies WHERE id=?", (sid,))
    conn.commit()
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════════
#  SALES
# ═══════════════════════════════════════════════════════════════════════════════

def add_sale(product_id, quantity, unit_price, discount=0, notes="", sale_date=None):
    if sale_date is None:
        sale_date = date.today().isoformat()
    total = (unit_price * quantity) - discount
    conn = get_conn()
    conn.execute("""
        INSERT INTO sales (product_id,quantity,unit_price,total,discount,notes,sale_date)
        VALUES (?,?,?,?,?,?,?)
    """, (product_id, quantity, unit_price, total, discount, notes, sale_date))
    conn.commit()
    conn.close()
    return total

def get_sales(product_id=None, from_date=None, to_date=None):
    conn = get_conn()
    q = """
        SELECT s.*, p.name as product_name, p.code as product_code
        FROM sales s LEFT JOIN products p ON s.product_id=p.id
        WHERE 1=1
    """
    params = []
    if product_id:
        q += " AND s.product_id=?"; params.append(product_id)
    if from_date:
        q += " AND s.sale_date>=?"; params.append(from_date)
    if to_date:
        q += " AND s.sale_date<=?"; params.append(to_date)
    q += " ORDER BY s.sale_date DESC, s.id DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return rows

def delete_sale(sid):
    conn = get_conn()
    conn.execute("DELETE FROM sales WHERE id=?", (sid,))
    conn.commit()
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════════
#  EXPENSES
# ═══════════════════════════════════════════════════════════════════════════════

def add_expense(description, amount, category="عام", expense_date=None):
    if expense_date is None:
        expense_date = date.today().isoformat()
    conn = get_conn()
    conn.execute("""
        INSERT INTO expenses (category,description,amount,expense_date)
        VALUES (?,?,?,?)
    """, (category, description, amount, expense_date))
    conn.commit()
    conn.close()

def get_expenses(from_date=None, to_date=None):
    conn = get_conn()
    q = "SELECT * FROM expenses WHERE 1=1"
    params = []
    if from_date:
        q += " AND expense_date>=?"; params.append(from_date)
    if to_date:
        q += " AND expense_date<=?"; params.append(to_date)
    q += " ORDER BY expense_date DESC, id DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return rows

def delete_expense(eid):
    conn = get_conn()
    conn.execute("DELETE FROM expenses WHERE id=?", (eid,))
    conn.commit()
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════════
#  DEBTS
# ═══════════════════════════════════════════════════════════════════════════════

def add_debt(debtor_name, amount, description="", debt_date=None, due_date=""):
    if debt_date is None:
        debt_date = date.today().isoformat()
    conn = get_conn()
    conn.execute("""
        INSERT INTO debts (debtor_name,amount,paid,description,debt_date,due_date,status)
        VALUES (?,?,0,?,?,?,'مفتوح')
    """, (debtor_name, amount, description, debt_date, due_date))
    conn.commit()
    conn.close()

def pay_debt(debt_id, amount, pay_date=None, notes=""):
    if pay_date is None:
        pay_date = date.today().isoformat()
    conn = get_conn()
    conn.execute("""
        INSERT INTO debt_payments (debt_id,amount,pay_date,notes)
        VALUES (?,?,?,?)
    """, (debt_id, amount, pay_date, notes))
    # تحديث المبلغ المدفوع والحالة
    conn.execute("""
        UPDATE debts SET paid = paid + ?
        WHERE id=?
    """, (amount, debt_id))
    conn.execute("""
        UPDATE debts SET status = CASE WHEN paid >= amount THEN 'مسدد' ELSE 'جزئي' END
        WHERE id=?
    """, (debt_id,))
    conn.commit()
    conn.close()

def get_debts(status=None):
    conn = get_conn()
    q = "SELECT * FROM debts WHERE 1=1"
    params = []
    if status:
        q += " AND status=?"; params.append(status)
    q += " ORDER BY debt_date DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return rows

def get_debt_payments(debt_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM debt_payments WHERE debt_id=? ORDER BY pay_date DESC",
        (debt_id,)
    ).fetchall()
    conn.close()
    return rows

def delete_debt(did):
    conn = get_conn()
    conn.execute("DELETE FROM debt_payments WHERE debt_id=?", (did,))
    conn.execute("DELETE FROM debts WHERE id=?", (did,))
    conn.commit()
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════════
#  CASHBOX  (محسوبة دائماً – لا تُخزَّن)
# ═══════════════════════════════════════════════════════════════════════════════

def get_cashbox_summary(from_date=None, to_date=None):
    conn = get_conn()
    params_f = [from_date] if from_date else []
    params_t = [to_date]   if to_date   else []

    def ranged(col):
        w = ""
        p = []
        if from_date: w += f" AND {col}>=?"; p.append(from_date)
        if to_date:   w += f" AND {col}<=?"; p.append(to_date)
        return w, p

    rng, prm = ranged("s.sale_date")
    sales_total = conn.execute(f"""
        SELECT COALESCE(SUM(s.total),0) 
        FROM sales s LEFT JOIN products p ON s.product_id=p.id
        WHERE 1=1 {rng}
    """, prm).fetchone()[0]

    rng, prm = ranged("expense_date")
    exp_total   = conn.execute(f"SELECT COALESCE(SUM(amount),0) FROM expenses WHERE 1=1{rng}", prm).fetchone()[0]

    rng, prm = ranged("pay_date")
    debt_paid   = conn.execute(f"SELECT COALESCE(SUM(amount),0) FROM debt_payments WHERE 1=1{rng}", prm).fetchone()[0]

    conn.close()
    net = sales_total + debt_paid - exp_total
    return {
        "sales":      sales_total,
        "expenses":   exp_total,
        "debt_paid":  debt_paid,
        "net":        net,
    }

# ═══════════════════════════════════════════════════════════════════════════════
#  INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════

def create_inventory_session(start_date, end_date, name="", notes=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO inventory_sessions (name,start_date,end_date,notes)
        VALUES (?,?,?,?)
    """, (name, start_date, end_date, notes))
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid

def save_inventory_item(session_id, product_id, actual_count, notes=""):
    conn = get_conn()
    # تحديث أو إدراج
    existing = conn.execute(
        "SELECT id FROM inventory_items WHERE session_id=? AND product_id=?",
        (session_id, product_id)
    ).fetchone()
    if existing:
        conn.execute("UPDATE inventory_items SET actual_count=?,notes=? WHERE id=?",
                     (actual_count, notes, existing["id"]))
    else:
        conn.execute("""
            INSERT INTO inventory_items (session_id,product_id,actual_count,notes)
            VALUES (?,?,?,?)
        """, (session_id, product_id, actual_count, notes))
    conn.commit()
    conn.close()

def get_inventory_sessions():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM inventory_sessions ORDER BY start_date DESC").fetchall()
    conn.close()
    return rows

def delete_inventory_session(sid):
    conn = get_conn()
    conn.execute("DELETE FROM inventory_items WHERE session_id=?", (sid,))
    conn.execute("DELETE FROM inventory_sessions WHERE id=?", (sid,))
    # التحقق إذا كان الجدول قد أصبح فارغاً لتصفير العداد
    count = conn.execute("SELECT COUNT(*) FROM inventory_sessions").fetchone()[0]
    if count == 0:
        conn.execute("DELETE FROM sqlite_sequence WHERE name='inventory_sessions'")
    conn.commit()
    conn.close()

def get_inventory_report(session_id):
    conn = get_conn()
    session = conn.execute("SELECT * FROM inventory_sessions WHERE id=?", (session_id,)).fetchone()
    if not session:
        conn.close()
        return None, []

    s_date, e_date = session["start_date"], session["end_date"]

    # 1. المبالغ المالية في هذه الفترة
    # إجمالي المبيعات (النقدية)
    total_sales_cash = conn.execute(
        "SELECT COALESCE(SUM(total), 0) FROM sales WHERE sale_date BETWEEN ? AND ?",
        (s_date, e_date)
    ).fetchone()[0]

    # إجمالي المصروفات
    total_expenses = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE expense_date BETWEEN ? AND ?",
        (s_date, e_date)
    ).fetchone()[0]

    # إجمالي الديون الجديدة (التي لم تُسدد بالكامل)
    total_new_debts = conn.execute(
        "SELECT COALESCE(SUM(amount - paid), 0) FROM debts WHERE debt_date BETWEEN ? AND ?",
        (s_date, e_date)
    ).fetchone()[0]

    # 2. تقرير الأصناف وحساب المبيعات "المفترضة" بناءً على النقص في الرفوف
    # جلب جميع الأصناف المسجلة (باستثناء المبيعات العامة) لتظهر في الجرد
    products = conn.execute("""
        SELECT id, code, name, unit, sell_price
        FROM products
        WHERE code != 'GENERAL'
        ORDER BY name
    """).fetchall()

    report = []
    total_implied_sales_value = 0.0

    for prod in products:
        pid = prod["id"]
        # كمية التوريد في هذه الفترة
        supplied = conn.execute(
            "SELECT COALESCE(SUM(quantity),0) FROM supplies WHERE product_id=? AND supply_date BETWEEN ? AND ?",
            (pid, s_date, e_date)
        ).fetchone()[0]
        
        # الكمية الفعلية المتبقية (التي أدخلها المستخدم)
        inv_row = conn.execute(
            "SELECT actual_count, notes FROM inventory_items WHERE session_id=? AND product_id=?",
            (session_id, pid)
        ).fetchone()
        actual = inv_row["actual_count"] if inv_row else None
        inv_notes = inv_row["notes"] if inv_row else ""
        
        # المبيعات "المفترضة" = ما تم توريده - ما تبقى على الرف
        # (بافتراض أن المخزن بدأ بـ 0 أو أننا نجرد التوريد الجديد فقط)
        implied_sold = (supplied - actual) if actual is not None else 0
        if implied_sold < 0: implied_sold = 0 # زيادة غير متوقعة
        
        # القيمة المالية لما خرج من الرف
        implied_value = implied_sold * prod["sell_price"]
        total_implied_sales_value += implied_value

        report.append({
            "product_id":   pid,
            "code":         prod["code"],
            "name":         prod["name"],
            "unit":         prod["unit"],
            "sell_price":   prod["sell_price"],
            "supplied":     supplied,
            "sold":         implied_sold, # هنا نعرض الكمية التي "اختفت" من الرف
            "expected":     supplied,     # المتوقع هو إجمالي ما تم توريده
            "actual":       actual,
            "deficit":      0,            # لم يعد هناك عجز قطع، بل عجز مالي إجمالي
            "deficit_value": implied_value,
            "inv_notes":    inv_notes,
        })

    conn.close()
    
    # 3. ملخص الجرد النهائي بناءً على مقارنة "الرف" بـ "الصندوق"
    # ما يجب أن يكون في الصندوق = (قيمة ما خرج من الرف) - (الديون) - (المصاريف)
    expected_cash_in_box = total_implied_sales_value - total_new_debts - total_expenses
    
    # العجز أو الفائض = (ما تم تسجيله فعلياً في المبيعات) - (ما يجب أن يكون في الصندوق)
    final_reconciliation = total_sales_cash - expected_cash_in_box
    
    summary = {
        "total_sales": total_sales_cash,     # ما سجله المستخدم بيده
        "total_expenses": total_expenses,
        "total_debts": total_new_debts,
        "physical_deficit_value": total_implied_sales_value, # قيمة البضاعة التي غادرت المحل
        "net_result": final_reconciliation    # الفرق النهائي (عجز/فائض مالي)
    }
    
    return session, report, summary

def delete_inventory_session(session_id):
    conn = get_conn()
    conn.execute("DELETE FROM inventory_items WHERE session_id=?", (session_id,))
    conn.execute("DELETE FROM inventory_sessions WHERE id=?", (session_id,))
    conn.commit()
    conn.close()

def delete_inventory_item(session_id, product_id):
    conn = get_conn()
    conn.execute("DELETE FROM inventory_items WHERE session_id=? AND product_id=?", (session_id, product_id))
    conn.commit()
    conn.close()

def reset_all_data():
    """
    حذف جميع البيانات من النظام والعودة للصفر (ضبط مصنع)
    """
    conn = get_conn()
    try:
        c = conn.cursor()
        # إيقاف التحقق من المفاتيح الأجنبية للسماح بالحذف الكامل
        c.execute("PRAGMA foreign_keys = OFF")
        
        # قائمة الجداول المراد حذفها
        tables = [
            "debt_payments", "debts", "expenses", "inventory_items", 
            "inventory_sessions", "sales", "supplies", "products"
        ]
        
        for table in tables:
            c.execute(f"DROP TABLE IF EXISTS {table}")
        
        # تصفير عدادات الترقيم التلقائي
        c.execute("DELETE FROM sqlite_sequence")
            
        conn.commit()
        # إعادة إنشاء الجداول من الصفر
        # ملاحظة: init_db سيتم استيرادها داخلياً أو نفترض وجودها
        init_db()
        return True
    except Exception as e:
        print(f"Database Reset Error: {e}")
        return False
    finally:
        conn.close()
