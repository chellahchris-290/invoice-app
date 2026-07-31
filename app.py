from flask import Flask, render_template, request, redirect
import sqlite3
import os
# PASTE THIS RIGHT AFTER your "import os" line
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

def send_reminder(invoice_id):
    conn = get_connection()
    invoice = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    conn.close()
    
    if not invoice:
        return
    
    # Get the customer email (if it exists in your customers table)
    conn = get_connection()
    customer = conn.execute("SELECT email FROM customers WHERE name = ?", (invoice['customer'],)).fetchone()
    conn.close()
    
    if not customer or not customer['email']:
        print(f"⚠️ No email found for {invoice['customer']}")
        return
    
    # Build the email
    subject = f"REMINDER: Invoice #{invoice['invoice_number']} is due"
    body = f"""
    Dear {invoice['customer']},
    
    This is a friendly reminder that invoice #{invoice['invoice_number']} for ${invoice['amount']} is outstanding.
    
    Please make payment at your earliest convenience.
    
    Thank you,
    Your Business Name
    """
    
    # SEND EMAIL (using a fake SMTP for now - we will set this up properly later)
    # For now, we just print it to the console so you can test
    print("="*50)
    print(f"📧 EMAIL TO: {customer['email']}")
    print(f"SUBJECT: {subject}")
    print(body)
    print("="*50)
    
    # Log that we sent it
    conn = get_connection()
    conn.execute("INSERT INTO reminders (invoice_id, reminder_type) VALUES (?, ?)", (invoice_id, "email"))
    conn.execute("UPDATE invoices SET reminder_sent = 1 WHERE id = ?", (invoice_id,))
    conn.commit()
    conn.close()

app = Flask(__name__)
DATABASE = "invoices.db"
print("Database being used:", os.path.abspath(DATABASE))


def get_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection

@app.route("/")
def home():
    connection = sqlite3.connect("invoices.db")
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM invoices")
    total_invoices = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COALESCE(SUM(grand_total), 0)
    FROM invoices
""")
    total_revenue = cursor.fetchone()[0]

    if total_revenue is None:
        total_revenue = 0

    cursor.execute("SELECT COUNT(DISTINCT customer) FROM invoices")
    total_customers = cursor.fetchone()[0]

    # 🔽 THIS IS THE NEW LINE YOU ADD 🔽
    cursor.execute("SELECT COUNT(*) FROM invoices WHERE status = 'Unpaid' AND due_date < date('now')")
    overdue_count = cursor.fetchone()[0]
    # 🔼 THE NEW LINE ENDS HERE 🔼

    cursor.execute("""
    SELECT id, customer, invoice_number, grand_total
    FROM invoices
    ORDER BY id DESC
    LIMIT 5
""")

    recent_invoices = cursor.fetchall()

    connection.close()

    return render_template(
        "index.html",
        total_invoices=total_invoices,
        total_revenue=total_revenue,
        total_customers=total_customers,
        recent_invoices=recent_invoices,
        overdue_count=overdue_count  # <--- ADD THIS LINE (note the comma at the end of the line above)
    )

@app.route("/invoice")
def invoice():
    return render_template("invoice.html")

@app.route("/preview", methods=["POST"])
def preview():
    customer = request.form["customer"]
    invoice_number = request.form["invoice_number"]
    amount = request.form["amount"]
    customer_email = request.form.get("customer_email", "")
    due_date = request.form.get("due_date", "")

    connection = sqlite3.connect("invoices.db")
    cursor = connection.cursor()

    cursor.execute(
    """
    INSERT INTO invoices
    (
        customer,
        customer_email,
        invoice_number,
        due_date,
        subtotal,
        tax_amount,
        grand_total,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        customer,
        customer_email,
        invoice_number,
        due_date,
        float(amount),
        0,
        float(amount),
        "Unpaid"
    )
)

    connection.commit()
    connection.close()

    return render_template(
        "preview.html",
        company_name="PayOps",
        company_phone="+260 977 123456",
        company_email="info@payops.com",
        company_address="Lusaka, Zambia",
        customer=customer,
        customer_email=customer_email,
        invoice_number=invoice_number,
        amount=amount,
        due_date=due_date
    )

@app.route("/invoices")
def invoices():

    connection = sqlite3.connect("invoices.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM invoices")

    invoices = cursor.fetchall()

    connection.close()

    return render_template(
        "invoices.html",
        invoices=invoices
    )
@app.route("/delete/<int:id>")
def delete_invoice(id):

    connection = sqlite3.connect("invoices.db")

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM invoices WHERE id=?",
        (id,)
    )

    connection.commit()

    connection.close()

    return redirect("/invoices")
@app.route("/settings")
def settings():

    return render_template("settings.html")
@app.route("/edit/<int:id>")
def edit_invoice(id):

    connection = sqlite3.connect("invoices.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, customer, invoice_number, amount FROM invoices WHERE id=?",
        (id,)
    )

    invoice = cursor.fetchone()
    connection.close()

    return render_template("edit_invoice.html", invoice=invoice)
@app.route("/update/<int:id>", methods=["POST"])
def update_invoice(id):

    customer = request.form["customer"]
    invoice_number = request.form["invoice_number"]
    amount = request.form["amount"]

    connection = sqlite3.connect("invoices.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE invoices
        SET customer=?, invoice_number=?, amount=?
        WHERE id=?
    """, (customer, invoice_number, amount, id))

    connection.commit()
    connection.close()

    return redirect("/invoices")
@app.route("/customers")
def customers():
    connection = sqlite3.connect("invoices.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, phone, email
        FROM customers
        ORDER BY name
    """)

    customers = cursor.fetchall()

    connection.close()

    return render_template(
        "customers.html",
        customers=customers
    )

@app.route("/add_customer", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        connection = sqlite3.connect("invoices.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO customers
            (name, phone, email, address)
            VALUES (?, ?, ?, ?)
        """, (name, phone, email, address))

        connection.commit()
        connection.close()

        return redirect("/customers")

    return render_template("add_customer.html")
@app.route("/estimates")
def estimates():

    connection = get_connection()

    estimates = connection.execute("""

        SELECT

            estimates.id,

            estimates.estimate_number,

            customers.name,

            estimates.status,

            estimates.total,

            estimates.valid_until

        FROM estimates

        LEFT JOIN customers

        ON estimates.client_id = customers.id

        ORDER BY estimates.id DESC

    """).fetchall()

    connection.close()

    return render_template(

        "estimates_list.html",

        estimates=estimates

    )
@app.route("/estimate")
def estimate():

    connection = get_connection()

    customers = connection.execute("""
        SELECT id, name
        FROM customers
        ORDER BY name
    """).fetchall()

    last_estimate = connection.execute("""
        SELECT estimate_number
        FROM estimates
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    if last_estimate:

        last_number = int(last_estimate["estimate_number"].split("-")[1])

        next_number = f"EST-{last_number + 1:06d}"

    else:

        next_number = "EST-000001"

    connection.close()

    return render_template(
        "estimate.html",
        customers=customers,
        estimate_number=next_number
    )

# PASTE THIS RIGHT BEFORE the "if __name__" line
def check_overdue_invoices():
    """This runs automatically to find overdue invoices and send reminders"""
    conn = get_connection()
    
    # Find invoices that are Unpaid, have a due_date, and haven't had a reminder sent
    overdue = conn.execute("""
        SELECT id FROM invoices 
        WHERE status = 'Unpaid' 
        AND due_date IS NOT NULL 
        AND due_date < date('now')
        AND reminder_sent = 0
    """).fetchall()
    
    conn.close()
    
    for inv in overdue:
        print(f"⏰ Invoice {inv['id']} is overdue! Sending reminder...")
        send_reminder(inv['id'])
@app.route("/save-estimate", methods=["POST"])
def save_estimate():

    connection = get_connection()

    customer_id = request.form["customer_id"]
    estimate_number = request.form["estimate_number"]
    valid_until = request.form["valid_until"]

    connection.execute(
        """
        INSERT INTO estimates
        (
            estimate_number,
            client_id,
            valid_until
        )
        VALUES (?, ?, ?)
        """,
        (
            estimate_number,
            customer_id,
            valid_until
        )
    )

    connection.commit()

    connection.close()

    return redirect("/estimate")
if __name__ == "__main__":
    app.run(debug=True)