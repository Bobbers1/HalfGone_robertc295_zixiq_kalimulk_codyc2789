# Zixi Qiao, Robert Chen, Kalimul Kaif, Cody Wong
# HalfGone
# SoftDev
# P04 - Makers Makin' It, Act II -- The Seequel
# 2026-04-20
# time spent: 1

from flask import Flask, render_template, redirect, url_for, request, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import yfinance as yf
import urllib.request
import json
import os

app = Flask(__name__)
app.secret_key = 'half_gone'

DATABASE = "database.db"

# -----------------------------
# Database Helper Funcs
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# Auth Routes
# -----------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            conn.close()

            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Username already exists.", "danger")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=session["user"])

@app.route("/explore")
@login_required
def explore():
    return render_template("explore.html")

# -----------------------------
#Stock Route
# -----------------------------
@app.route("/stock")
@login_required
def stock():
    ticker = request.args.get("ticker")
    compare = request.args.get("compare")

    if not ticker:
        return redirect(url_for("dashboard"))

    try:
        def fetch(t):
            data = yf.Ticker(t)
            hist = data.history(period="5y", interval="1d", auto_adjust=True, prepost=False)
            if hist.empty:
                raise ValueError(f"Invalid ticker or no data found for {t.upper()}.")
            return hist

        hist1 = fetch(ticker)

        # Compare mode
        if compare:
            hist2 = fetch(compare)
            common_dates = hist1.index.intersection(hist2.index)
            hist1 = hist1.loc[common_dates]
            hist2 = hist2.loc[common_dates]
            dates = common_dates.strftime('%Y-%m-%d').tolist()
            closes2 = hist2['Close'].round(2).tolist()
            high2 = round(hist2['High'].max(), 2)
            low2 = round(hist2['Low'].min(), 2)
            avg_vol2 = f"{int(hist2['Volume'].mean()):,}"
            latest2 = closes2[-1]
        else:
            dates = hist1.index.strftime('%Y-%m-%d').tolist()
            closes2 = high2 = low2 = avg_vol2 = latest2 = None

        closes1 = hist1['Close'].round(2).tolist()

        return render_template(
            "stock_viewer.html",
            ticker=ticker.upper(),
            compare=compare.upper() if compare else None,
            dates=dates,
            closes1=closes1,
            closes2=closes2,
            latest_price=closes1[-1],
            latest2=latest2,
            high=round(hist1['High'].max(), 2),
            high2=high2,
            low=round(hist1['Low'].min(), 2),
            low2=low2,
            avg_volume=f"{int(hist1['Volume'].mean()):,}",
            avg_vol2=avg_vol2,
        )

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("explore"))
    except Exception:
        flash("Error fetching stock data.", "danger")
        return redirect(url_for("explore"))

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
