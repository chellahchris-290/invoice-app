def calculate_totals(items, tax_rate=16, discount=0):
    """
    items = [
        {"qty":2,"price":500},
        {"qty":1,"price":300}
    ]
    """

    subtotal = 0

    for item in items:
        subtotal += item["qty"] * item["price"]

    subtotal -= discount

    tax = subtotal * (tax_rate / 100)

    grand_total = subtotal + tax

    return {
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "discount": round(discount, 2),
        "grand_total": round(grand_total, 2)
    }