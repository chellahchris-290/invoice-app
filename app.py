from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/invoice")
def invoice():
    return render_template("invoice.html")

@app.route("/preview", methods=["POST"])
def preview():

    customer = request.form["customer"]
    invoice_number = request.form["invoice_number"]
    amount = request.form["amount"]
    connection = sqlite3.connect("invoices.db")

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO invoices
        (customer, invoice_number, amount)
        VALUES (?, ?, ?)
        """,
        (customer, invoice_number, amount)
    )

    connection.commit()

    connection.close()

    return render_template(
        "preview.html",
        customer=customer,
        invoice_number=invoice_number,
        amount=amount
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
if __name__ == "__main__":
    app.run(debug=True)