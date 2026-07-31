import sqlite3

conn = sqlite3.connect("invoices.db")
cursor = conn.cursor()

# Add each column one by one, safely catching errors if they already exist
columns_to_add = [
    ("status", "TEXT DEFAULT 'Unpaid'"),
    ("due_date", "TEXT"),
    ("customer_email", "TEXT"),
    ("reminder_sent", "INTEGER DEFAULT 0")
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE invoices ADD COLUMN {col_name} {col_type}")
        print(f"✅ Added column: {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"⏩ Column already exists, skipping: {col_name}")
        else:
            print(f"⚠️ Error: {e}")

conn.commit()
conn.close()
print("🎉 Database fix complete! Now run your Flask app.") 