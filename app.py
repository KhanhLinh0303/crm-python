from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# =====================
# DATABASE
# =====================

def get_db():
    return sqlite3.connect('crm.db')

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total REAL,
        date TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

# =====================
# ROUTES
# =====================

@app.route('/')
def dashboard():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT SUM(total) FROM orders")
    revenue = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM customers")
    customers = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM orders")
    orders = c.fetchone()[0]

    conn.close()

    return render_template('dashboard.html', revenue=revenue, customers=customers, orders=orders)

# ----- Customers -----
@app.route('/customers')
def customers():
    conn = get_db()
    data = conn.execute("SELECT * FROM customers").fetchall()
    conn.close()
    return render_template('customers.html', customers=data)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    conn = get_db()
    conn.execute("INSERT INTO customers (name) VALUES (?)", (request.form['name'],))
    conn.commit()
    conn.close()
    return redirect('/customers')

# ----- Products -----
@app.route('/products')
def products():
    conn = get_db()
    data = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('products.html', products=data)

@app.route('/add_product', methods=['POST'])
def add_product():
    conn = get_db()
    conn.execute("INSERT INTO products (name, price) VALUES (?, ?)",
                 (request.form['name'], request.form['price']))
    conn.commit()
    conn.close()
    return redirect('/products')

# ----- Orders -----
@app.route('/orders')
def orders():
    conn = get_db()

    orders = conn.execute("""
        SELECT orders.id, customers.name, products.name, orders.quantity, orders.total
        FROM orders
        JOIN customers ON customers.id = orders.customer_id
        JOIN products ON products.id = orders.product_id
    """).fetchall()

    customers = conn.execute("SELECT * FROM customers").fetchall()
    products = conn.execute("SELECT * FROM products").fetchall()

    conn.close()

    return render_template('orders.html', orders=orders, customers=customers, products=products)

@app.route('/add_order', methods=['POST'])
def add_order():
    conn = get_db()

    customer_id = request.form['customer_id']
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])

    price = conn.execute("SELECT price FROM products WHERE id=?", (product_id,)).fetchone()[0]
    total = price * quantity

    conn.execute("""
        INSERT INTO orders (customer_id, product_id, quantity, total, date)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, product_id, quantity, total, datetime.now()))

    conn.commit()
    conn.close()
    return redirect('/orders')

# =====================
# RUN
# =====================
if __name__ == '__main__':
    app.run(debug=True)