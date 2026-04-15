# Zixi Qiao, Robert Chen, Kalimul Kaif, Cody Wong
# HalfGone
# SoftDev
# P04 - Makers Makin' It, Act II -- The Seequel
# 2026-04-20
# time spent: 1

from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import yfinance as yf
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

FAANG_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA"]

TICKER_NAMES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet",
    "META": "Meta",
    "NVDA": "NVIDIA",
}

@app.route("/api/stocks")
@login_required
def api_stocks():
    result = []
    for symbol in FAANG_TICKERS:
        try:
            info = yf.Ticker(symbol).fast_info
            price = round(float(info.last_price), 2)
            prev = round(float(info.previous_close), 2)
            change = round((price - prev) / prev * 100, 2) if prev else 0.0
            result.append({
                "ticker": symbol,
                "name": TICKER_NAMES.get(symbol, symbol),
                "price": price,
                "change": change,
            })
        except Exception:
            result.append({
                "ticker": symbol,
                "name": TICKER_NAMES.get(symbol, symbol),
                "price": None,
                "change": None,
            })
    return jsonify(result)

@app.route("/api/search")
@login_required
def api_search():
    ticker = request.args.get("ticker", "").upper().strip()
    if not ticker:
        return jsonify({"error": "Please provide a ticker symbol."}), 400
    try:
        info = yf.Ticker(ticker).fast_info
        price = round(float(info.last_price), 2)
        prev = round(float(info.previous_close), 2)
        change = round((price - prev) / prev * 100, 2) if prev else 0.0
        return jsonify({"ticker": ticker, "price": price, "change": change})
    except Exception:
        return jsonify({"error": "Couldn't find that stock. Try a different ticker."}), 404


@app.route("/stock")
@login_required
def stock():
    ticker = request.args.get("ticker")

    if not ticker:
        return redirect(url_for("dashboard"))

    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="5y")

        if hist.empty:
            flash("Invalid ticker or no data found.", "danger")
            return redirect(url_for("dashboard"))

        dates = hist.index.strftime('%Y-%m-%d').tolist()
        closes = hist['Close'].round(2).tolist()

        return render_template(
            "stock_viewer.html",
            ticker=ticker.upper(),
            dates=dates,
            closes=closes,
            latest_close=closes[-1],
            high=round(hist['High'].max(), 2),
            low=round(hist['Low'].min(), 2),
            avg_volume=f"{int(hist['Volume'].mean()):,}"
        )

    except Exception:
        flash("Error fetching stock data.", "danger")
        return redirect(url_for("dashboard"))

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)