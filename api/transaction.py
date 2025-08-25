from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from config import get_db_connection
from datetime import datetime

bp = Blueprint("transaction", __name__, url_prefix="/transaction")


@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT balance FROM accounts WHERE user_id=%s", (session["user_id"],))
    account = cursor.fetchone()

    cursor.execute("SELECT * FROM transactions WHERE user_id=%s ORDER BY date DESC", (session["user_id"],))
    history = cursor.fetchall()

    conn.close()
    return render_template("dashboard.html", balance=account["balance"], history=history)


@bp.route("/deposit", methods=["POST"])
def deposit():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    amount = float(request.form["amount"])
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE user_id=%s", (amount, session["user_id"]))
    cursor.execute("INSERT INTO transactions (user_id, type, amount, date) VALUES (%s, %s, %s, %s)",
                   (session["user_id"], "Deposit", amount, datetime.now()))

    conn.commit()
    conn.close()
    flash("Deposit successful!", "success")
    return redirect(url_for("transaction.dashboard"))


@bp.route("/withdraw", methods=["POST"])
def withdraw():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    amount = float(request.form["amount"])
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT balance FROM accounts WHERE user_id=%s", (session["user_id"],))
    account = cursor.fetchone()

    if account["balance"] >= amount:
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE user_id=%s", (amount, session["user_id"]))
        cursor.execute("INSERT INTO transactions (user_id, type, amount, date) VALUES (%s, %s, %s, %s)",
                       (session["user_id"], "Withdraw", amount, datetime.now()))
        conn.commit()
        flash("Withdrawal successful!", "success")
    else:
        flash("Insufficient balance!", "danger")

    conn.close()
    return redirect(url_for("transaction.dashboard"))
