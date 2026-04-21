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
from functools import wraps
import os

import pandas as pd
import numpy as np

# Try to import yfinance
try:
    import yfinance as yf
except Exception:
    yf = None
import build_db

app = Flask(__name__)
app.secret_key = "half_gone"

DATABASE = os.path.join(os.path.dirname(__file__), "..", "data.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "static", "faang_stock_prices.csv")
SUPPLY_CHAIN_COMPANIES = {
    "TSM": "Taiwan Semiconductor",
    "NVDA": "NVIDIA",
    "TSLA": "Tesla",
}


def get_server_port():
    return int(os.environ.get("PORT", "5001"))


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
build_db.main()


def load_dataset_frame():
    df = pd.read_csv(CSV_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    return df.sort_values(["Ticker", "Date"])


def get_dataset_history(ticker):
    rows = build_db.get_stock_data_from_csv(ticker)
    if not rows:
        raise ValueError(f"Invalid ticker or no dataset found for {ticker.upper()}.")

    frame = pd.DataFrame(rows)
    frame["Date"] = pd.to_datetime(frame["Date"])
    frame = frame.sort_values("Date")
    for column in ("Close", "High", "Low", "Volume"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def get_stock_history(ticker):
    ticker = ticker.upper()
    if yf is not None:
        try:
            data = yf.Ticker(ticker)
            hist = data.history(
                period="5y", interval="1d", auto_adjust=True, prepost=False
            )
            if not hist.empty:
                return hist, "yfinance"
        except Exception:
            pass

    dataset_hist = get_dataset_history(ticker)
    dataset_hist = dataset_hist.set_index("Date")
    return dataset_hist, "dataset"


def summarize_history(hist):
    closes = hist["Close"].dropna().round(2).tolist()
    if not closes:
        raise ValueError("No close price data available.")

    dates = hist.index.strftime("%Y-%m-%d").tolist()
    high = round(hist["High"].dropna().max(), 2)
    low = round(hist["Low"].dropna().min(), 2)
    avg_volume = hist["Volume"].dropna().mean()

    return {
        "dates": dates,
        "closes": closes,
        "high": high,
        "low": low,
        "latest_price": closes[-1],
        "avg_volume": f"{int(avg_volume):,}" if pd.notna(avg_volume) else "N/A",
    }


def get_market_snapshot(ticker):
    try:
        hist, source = get_stock_history(ticker)
        summary = summarize_history(hist)
        latest_close = summary["latest_price"]

        prev_close = None
        if len(hist["Close"].dropna()) >= 2:
            prev_close = float(hist["Close"].dropna().iloc[-2])

        change = None
        if prev_close and prev_close != 0:
            change = round(latest_close - prev_close, 2)

        price = latest_close
    except ValueError:
        source = "unavailable"
        price = None
        change = None

    return {
        "symbol": ticker.upper(),
        "name": SUPPLY_CHAIN_COMPANIES.get(ticker.upper(), ticker.upper()),
        "price": price,
        "change": change,
        "source": source,
    }


def get_live_stock_history(ticker):
    if yf is None:
        raise ValueError("Live market data is unavailable because yfinance is not installed correctly.")

    data = yf.Ticker(ticker.upper())
    hist = data.history(period="6mo", interval="1d", auto_adjust=True, prepost=False)
    if hist.empty:
        raise ValueError(f"Live market data is unavailable for {ticker.upper()}.")
    return hist.sort_index()


def get_supply_chain_context():
    tickers = ["TSM", "NVDA", "TSLA"]
    colors = {"TSM": "rgb(59, 130, 246)", "NVDA": "rgb(132, 204, 22)", "TSLA": "rgb(239, 68, 68)"}
    stocks = []
    stock_charts = []

    for ticker in tickers:
        hist = get_live_stock_history(ticker)
        source = "yfinance"

        close_series = hist["Close"].dropna()
        if close_series.empty:
            raise ValueError(f"Missing close price data for {ticker}.")

        latest_close = round(float(close_series.iloc[-1]), 2)
        prev_close = float(close_series.iloc[-2]) if len(close_series) >= 2 else None
        change = round(latest_close - prev_close, 2) if prev_close not in (None, 0) else None

        stocks.append(
            {
                "symbol": ticker,
                "name": SUPPLY_CHAIN_COMPANIES[ticker],
                "price": latest_close,
                "change": change,
                "source": source,
            }
        )

        recent_hist = hist.sort_index().tail(180)
        closes = recent_hist["Close"].dropna()
        if closes.empty:
            raise ValueError(f"Missing recent close price data for {ticker}.")

        volume_series = recent_hist["Volume"].dropna()
        if volume_series.empty:
            raise ValueError(f"Missing volume data for {ticker}.")

        labels = recent_hist.index.strftime("%b %d").tolist()
        stock_charts.append(
            {
                "ticker": ticker,
                "name": SUPPLY_CHAIN_COMPANIES[ticker],
                "labels": labels,
                "price_data": closes.round(2).tolist(),
                "volume_data": volume_series.round(2).tolist(),
                "color": colors[ticker],
                "source": source,
            }
        )

    return {
        "stocks": stocks,
        "stock_charts": stock_charts,
    }


def get_dashboard_context():
    df = load_dataset_frame()
    tickers = sorted(df["Ticker"].str.upper().unique().tolist())
    latest_date = df["Date"].max()
    recent = df[df["Date"] >= (latest_date - pd.Timedelta(days=365))].copy()
    tracked_tickers = [ticker for ticker in ["AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA"] if ticker in tickers]

    growth_labels = []
    growth_series = []
    volume_labels = []
    volume_series = []

    for ticker in tracked_tickers:
        ticker_df = recent[recent["Ticker"].str.upper() == ticker].sort_values("Date")
        monthly = ticker_df.set_index("Date")["Close"].resample("ME").last().dropna()
        if monthly.empty:
            continue

        base = monthly.iloc[0]
        indexed = ((monthly / base) * 100).round(2)
        if not growth_labels:
            growth_labels = indexed.index.strftime("%b %Y").tolist()

        growth_series.append(
            {
                "label": ticker,
                "data": indexed.tolist(),
            }
        )

        monthly_volume = ticker_df.set_index("Date")["Volume"].resample("ME").mean().dropna()
        if not monthly_volume.empty:
            if not volume_labels:
                volume_labels = monthly_volume.index.strftime("%b %Y").tolist()

            volume_series.append(
                {
                    "label": ticker,
                    "data": monthly_volume.round(2).tolist(),
                }
            )

    latest_rows = df.sort_values("Date").groupby("Ticker").tail(1)
    market_return = latest_rows["Daily_Return"].dropna().mean()
    avg_volume = latest_rows["Volume"].dropna().mean()

    return {
        "growth_labels": growth_labels,
        "growth_series": growth_series,
        "volume_labels": volume_labels,
        "volume_series": volume_series,
        "stats": {
            "market_return": f"{market_return * 100:+.2f}%" if pd.notna(market_return) else "N/A",
            "stocks_tracked": len(tickers),
            "avg_volume": f"{int(avg_volume):,}" if pd.notna(avg_volume) else "N/A",
        },
    }


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


@app.route("/dashboard_data")
@login_required
def get_dashboard_data():
    try:
        return jsonify(get_dashboard_context())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/explore")
@login_required
def explore():
    return render_template("explore.html")


# -----------------------------
# Supply Chain Route
# -----------------------------
@app.route("/supply-chain")
@login_required
def supply_chain():
    return render_template("supply_chain.html")


@app.route("/supply_chain_data")
@login_required
def get_supply_chain_data():
    try:
        return jsonify(get_supply_chain_context())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

    try:
        hist1, source1 = get_stock_history(ticker)
        summary1 = summarize_history(hist1)

        if compare:
            hist2, source2 = get_stock_history(compare)
            common_dates = hist1.index.intersection(hist2.index)
            hist1 = hist1.loc[common_dates]
            hist2 = hist2.loc[common_dates]

            if hist1.empty or hist2.empty:
                raise ValueError("These tickers do not have overlapping data to compare.")

            summary1 = summarize_history(hist1)
            summary2 = summarize_history(hist2)
            dates = summary1["dates"]
            closes2 = summary2["closes"]
            high2 = summary2["high"]
            low2 = summary2["low"]
            avg_vol2 = summary2["avg_volume"]
            latest2 = summary2["latest_price"]
        else:
            source2 = None
            dates = summary1["dates"]
            closes2 = high2 = low2 = avg_vol2 = latest2 = None

        closes1 = summary1["closes"]
        high = summary1["high"]
        low = summary1["low"]
        latest_price = summary1["latest_price"]
        avg_volume = summary1["avg_volume"]
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
        data_source=source1,
        compare_source=source2,
    )


@app.route("/analysis", methods=["GET"])
@login_required
def analysis():
    return render_template("analysis.html", user=session["user"])


@app.route("/analysis_data")
@login_required
def get_analysis_data():
    try:
        conn = get_db_connection()

        query = """
        SELECT
            sd.date as Date,
            s.ticker as Ticker,
            sd.close_price as Close,
            sd.returns as Daily_Return
        FROM stock_data sd
        JOIN stocks s ON sd.stock_id = s.id
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        df["Date"] = pd.to_datetime(df["Date"])

        # Last 2 years
        latest_date = df["Date"].max()
        two_years_ago = latest_date - pd.Timedelta(days=730)
        df_recent = df[df["Date"] >= two_years_ago].copy()

        # Pivot returns
        pivot_returns = df_recent.pivot(
            index="Date", columns="Ticker", values="Daily_Return"
        )

        # Correlation
        corr_matrix = pivot_returns.corr()
        tickers = corr_matrix.index.tolist()

        correlation_data = []
        for t1 in tickers:
            for t2 in tickers:
                correlation_data.append(
                    {"x": t1, "y": t2, "value": round(corr_matrix.loc[t1, t2], 3)}
                )

        # Risk-adjusted metrics
        risk_adjusted = []

        for ticker in pivot_returns.columns:
            returns = pivot_returns[ticker].dropna()

            mean_return = returns.mean() * 252  # number of trading days in a year
            volatility = returns.std() * np.sqrt(252)
            risk_free_rate = 0.037  # currently 3.7% 3 month treasury rate

            sharpe_ratio = (
                (mean_return - risk_free_rate) / volatility if volatility > 0 else 0
            )

            ticker_data = df_recent[df_recent["Ticker"] == ticker].sort_values("Date")

            if len(ticker_data) > 0:
                initial_price = ticker_data.iloc[0]["Close"]
                final_price = ticker_data.iloc[-1]["Close"]
                total_return = ((final_price / initial_price) - 1) * 100
            else:
                total_return = 0

            risk_adjusted.append(
                {
                    "ticker": ticker,
                    "sharpe_ratio": round(sharpe_ratio, 3),
                    "annual_return": round(mean_return * 100, 2),
                    "annual_volatility": round(volatility * 100, 2),
                    "total_return": round(total_return, 2),
                }
            )

        risk_adjusted.sort(key=lambda x: x["sharpe_ratio"], reverse=True)

        return jsonify(
            {
                "correlation": {"tickers": tickers, "data": correlation_data},
                "risk_adjusted": risk_adjusted,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=get_server_port())
