import sqlite3

connection = sqlite3.connect("invoices.db")
cursor = connection.cursor()

columns = [

    ("tenant_id", "INTEGER DEFAULT 1"),
    ("issue_date", "DATE DEFAULT CURRENT_DATE"),
    ("valid_until", "DATE"),
    ("subtotal", "REAL DEFAULT 0"),
    ("discount", "REAL DEFAULT 0"),
    ("tax_rate", "REAL DEFAULT 16"),
    ("tax_amount", "REAL DEFAULT 0"),
    ("grand_total", "REAL DEFAULT 0"),
    ("currency", "TEXT DEFAULT 'ZMW'"),
    ("notes", "TEXT"),
    ("terms", "TEXT"),
    ("public_token", "TEXT"),
    ("approved_at", "TIMESTAMP"),
    ("converted_at", "TIMESTAMP")

]

for name, definition in columns:

    try:

        cursor.execute(
            f"ALTER TABLE estimates ADD COLUMN {name} {definition}"
        )

        print(f"✓ Added {name}")

    except sqlite3.OperationalError:

        print(f"- {name} already exists")

connection.commit()
connection.close()

print("\nMigration completed successfully.")