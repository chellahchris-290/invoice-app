import sqlite3

connection = sqlite3.connect("invoices.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT,
    invoice_number TEXT,
    amount REAL
)
""")

connection.commit()

connection.close()

print("Database created successfully.")