from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DB_NAME = "database.db"


# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE TABLE ----------------
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            total_amount REAL NOT NULL,
            amount_paid REAL DEFAULT 0,
            lending_date TEXT,
            paying_date TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ---------------- HOME PAGE ----------------
@app.route('/')
def index():
    conn = get_db_connection()
    debts = conn.execute("SELECT * FROM debts").fetchall()

    total_lent = conn.execute("SELECT SUM(total_amount) FROM debts").fetchone()[0] or 0
    total_received = conn.execute("SELECT SUM(amount_paid) FROM debts").fetchone()[0] or 0
    total_remaining = total_lent - total_received

    conn.close()

    return render_template("index.html",
                           debts=debts,
                           total_lent=total_lent,
                           total_received=total_received,
                           total_remaining=total_remaining)


# ---------------- ADD DEBT ----------------
@app.route('/add', methods=['POST'])
def add_debt():
    name = request.form['name']
    amount = float(request.form['amount'])
    lending_date = request.form['lending_date']

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO debts (name, total_amount, lending_date) VALUES (?, ?, ?)",
        (name, amount, lending_date)
    )
    conn.commit()
    conn.close()

    return redirect('/')


# ---------------- UPDATE PAYMENT ----------------
@app.route('/pay/<int:id>', methods=['POST'])
def update_payment(id):
    amount_paid = float(request.form['amount_paid'])
    paying_date = request.form['paying_date']

    conn = get_db_connection()
    debt = conn.execute("SELECT * FROM debts WHERE id = ?", (id,)).fetchone()

    new_paid = debt['amount_paid'] + amount_paid

    conn.execute("""
        UPDATE debts 
        SET amount_paid = ?, paying_date = ?
        WHERE id = ?
    """, (new_paid, paying_date, id))

    conn.commit()
    conn.close()

    return redirect('/')


# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM debts WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
