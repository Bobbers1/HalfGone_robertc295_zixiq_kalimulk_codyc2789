# Zixi Qiao, Robert Chen, Kalimul Kaif, Cody Wong
# HalfGone
# SoftDev
# P04 - Makers Makin' It, Act II -- The Seequel
# 2026-04-20
# time spent: 1

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    jsonify,
)
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Try to import yfinance
try:
    import yfinance as yf
except ImportError:
    yf = None
    print("Warning: yfinance not available")

# Mock data fallback
MOCK_DATA = {
    "AAPL": [100, 105, 103, 110, 115, 120, 118, 125, 130, 128],
    "MSFT": [100, 102, 105, 108, 110, 112, 115, 118, 120, 125],
    "NVDA": [100, 110, 115, 125, 130, 140, 135, 150, 160, 170],
}
import urllib.request
import json
import csv
import os

app = Flask(__name__)
app.secret_key = "half_gone"

DATABASE = "database.db"
CSV_PATH = os.path.join(os.path.dirname(__file__), "static", "faang_stock_prices.csv")


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


# Params:
# ticker: stock id
# limit: number of entries (eg. 30 = last 30 days)
# Returns: list of dicts, each containing stock data on a certain day
# DO NOT move this function definition, must happen after init_db()
def get_stock_data_from_csv(ticker: str, limit: int = None) -> list[dict]:
    ticker = ticker.upper()
    results = []

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Ticker"].upper() == ticker:
                for col in (
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                    "SMA_7",
                    "SMA_21",
                    "EMA_12",
                    "EMA_26",
                    "RSI_14",
                    "MACD",
                    "MACD_Signal",
                    "Bollinger_Upper",
                    "Bollinger_Lower",
                    "Daily_Return",
                    "Volatility_7d",
                    "Next_Day_Close",
                ):
                    try:
                        row[col] = float(row[col]) if row[col] else None
                    except ValueError:
                        row[col] = None
                results.append(row)

    results.sort(key=lambda r: r["Date"], reverse=True)

    return results[:limit] if limit is not None else results


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
                (username, hashed_password),
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
# Supply Chain Route (Stage 1 - basic)
# -----------------------------
@app.route("/supply-chain")
@login_required
def supply_chain():
    """Simple supply chain view - TSM → NVDA → TSLA"""
    stocks = [
        {
            "symbol": "TSM",
            "name": "Taiwan Semiconductor",
            "price": 107.89,
            "change": 2.34,
        },
        {"symbol": "NVDA", "name": "NVIDIA", "price": 495.22, "change": 12.45},
        {"symbol": "TSLA", "name": "Tesla", "price": 248.50, "change": -5.20},
    ]
    return render_template("supply_chain.html", stocks=stocks)


# -----------------------------
# Stock Route
# -----------------------------
@app.route("/stock")
@login_required
def stock():
    ticker = request.args.get("ticker")
    compare = request.args.get("compare")

    if not ticker:
        return redirect(url_for("dashboard"))

        # Use mock data if yfinance not available
        if yf is None:
            closes1 = MOCK_DATA.get(
                ticker.upper(), [100, 105, 110, 115, 120, 125, 130, 135, 140, 145]
            )
            dates = [
                "2024-01",
                "2024-02",
                "2024-03",
                "2024-04",
                "2024-05",
                "2024-06",
                "2024-07",
                "2024-08",
                "2024-09",
                "2024-10",
            ]
            closes2 = None
            high = max(closes1)
            low = min(closes1)
            latest_price = closes1[-1]
            avg_volume = "50,000,000"
            high2 = low2 = avg_vol2 = latest2 = None
        else:
            try:

                def fetch(t):
                    data = yf.Ticker(t)
                    hist = data.history(
                        period="5y", interval="1d", auto_adjust=True, prepost=False
                    )
                    if hist.empty:
                        raise ValueError(
                            f"Invalid ticker or no data found for {t.upper()}."
                        )
                    return hist

                hist1 = fetch(ticker)

                # Compare mode
                if compare:
                    hist2 = fetch(compare)
                    common_dates = hist1.index.intersection(hist2.index)
                    hist1 = hist1.loc[common_dates]
                    hist2 = hist2.loc[common_dates]
                    dates = common_dates.strftime("%Y-%m-%d").tolist()
                    closes2 = hist2["Close"].round(2).tolist()
                    high2 = round(hist2["High"].max(), 2)
                    low2 = round(hist2["Low"].min(), 2)
                    avg_vol2 = f"{int(hist2['Volume'].mean()):,}"
                    latest2 = closes2[-1]
                else:
                    dates = hist1.index.strftime("%Y-%m-%d").tolist()
                    closes2 = high2 = low2 = avg_vol2 = latest2 = None

                closes1 = hist1["Close"].round(2).tolist()
                high = round(hist1["High"].max(), 2)
                low = round(hist1["Low"].min(), 2)
                latest_price = closes1[-1]
                avg_volume = f"{int(hist1['Volume'].mean()):,}"
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(url_for("explore"))
            except Exception:
                flash("Error fetching stock data.", "danger")
                return redirect(url_for("explore"))

        return render_template(
            "stock_viewer.html",
            ticker=ticker.upper(),
            compare=compare.upper() if compare else None,
            dates=dates,
            closes1=closes1,
            closes2=closes2,
            latest_price=latest_price,
            latest2=latest2,
            high=high,
            high2=high2,
            low=low,
            low2=low2,
            avg_volume=avg_volume,
            avg_vol2=avg_vol2,
        )


# -----------------------------
# Analysis Route
# -----------------------------
@app.route("/analysis")
@login_required
def analysis():
    return render_template("analysis.html")


@app.route("/analysis_data")
@login_required
def analysis_data():
    stocks = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA"]

    # Generate correlation data
    corr_data = []
    for i, s1 in enumerate(stocks):
        for j, s2 in enumerate(stocks):
            if i == j:
                corr_data.append({"x": s2, "y": s1, "value": 1.0})
            else:
                val = 0.3 + (hash(s1 + s2) % 70) / 100
                corr_data.append({"x": s2, "y": s1, "value": round(val, 2)})

    # Generate risk-adjusted data (mock Sharpe ratios)
    risk_adjusted = []
    for s in stocks:
        risk_adjusted.append(
            {
                "ticker": s,
                "sharpe_ratio": round(0.5 + (hash(s) % 150) / 100, 2),
                "return": round(5 + (hash(s) % 30), 2),
                "risk": round(10 + (hash(s + "x") % 20), 2),
            }
        )

    return jsonify(
        {
            "correlation": {"data": corr_data, "tickers": stocks},
            "risk_adjusted": risk_adjusted,
        }
    )


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5003)
