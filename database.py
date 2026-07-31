import sqlite3

DATABASE = "invoices.db"

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()
# =====================================================
# CUSTOMERS
# =====================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    company TEXT,

    email TEXT,

    phone TEXT,

    address TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")
# =====================================================
# INVOICES
# =====================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    customer TEXT NOT NULL,

    customer_email TEXT,

    invoice_number TEXT UNIQUE NOT NULL,

    issue_date DATE DEFAULT CURRENT_DATE,

    due_date DATE,

    subtotal REAL DEFAULT 0,

    discount REAL DEFAULT 0,

    tax_name TEXT DEFAULT 'VAT',

    tax_rate REAL DEFAULT 0,

    tax_amount REAL DEFAULT 0,

    grand_total REAL DEFAULT 0,

    currency TEXT DEFAULT 'ZMW',

    status TEXT DEFAULT 'Draft',

    notes TEXT,

    terms TEXT,

    reminder_sent INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")
# =====================================================
# INVOICE ITEMS
# =====================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoice_items (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    invoice_id INTEGER NOT NULL,

    description TEXT NOT NULL,

    quantity REAL DEFAULT 1,

    unit_price REAL DEFAULT 0,

    discount REAL DEFAULT 0,

    tax_rate REAL DEFAULT 0,

    line_total REAL DEFAULT 0,

    FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE

)
""")
# =====================================================
# ESTIMATES
# =====================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS estimates (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    estimate_number TEXT UNIQUE NOT NULL,

    client_id INTEGER NOT NULL,

    title TEXT,

    notes TEXT,

    subtotal REAL DEFAULT 0,

    discount REAL DEFAULT 0,

    tax_name TEXT DEFAULT 'VAT',

    tax_rate REAL DEFAULT 0,

    tax_amount REAL DEFAULT 0,

    total REAL DEFAULT 0,

    currency TEXT DEFAULT 'ZMW',

    status TEXT DEFAULT 'Draft',

    valid_until DATE,

    public_token TEXT,

    viewed_at DATETIME,

    approved_at DATETIME,

    rejected_at DATETIME,

    converted_invoice_id INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(client_id) REFERENCES customers(id)

)
""")

# =====================================================
# ESTIMATE ITEMS
# =====================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS estimate_items (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    estimate_id INTEGER NOT NULL,

    description TEXT NOT NULL,

    quantity REAL DEFAULT 1,

    unit_price REAL DEFAULT 0,

    discount REAL DEFAULT 0,

    tax_rate REAL DEFAULT 0,

    line_total REAL DEFAULT 0,

    FOREIGN KEY(estimate_id) REFERENCES estimates(id) ON DELETE CASCADE

)
""")

# =====================================================
# SETTINGS
# =====================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company_name TEXT,

    company_email TEXT,

    company_phone TEXT,

    company_address TEXT,

    currency TEXT DEFAULT 'ZMW',

    tax_name TEXT DEFAULT 'VAT',

    tax_rate REAL DEFAULT 0

)
""")

# =====================================================
# PAYMENTS
# =====================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    invoice_id INTEGER,

    amount REAL,

    payment_date DATE,

    method TEXT,

    reference TEXT,

    FOREIGN KEY(invoice_id) REFERENCES invoices(id)

)
""")

# =====================================================
# REMINDERS
# =====================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    invoice_id INTEGER,

    reminder_type TEXT,

    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(invoice_id) REFERENCES invoices(id)

)
""")

# =====================================================
# ACTIVITY LOG
# =====================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS activity_log (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    action TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

connection.commit()
connection.close()

print("Database created successfully.")