# Zixi Qiao, Robert Chen, Kalimul Kaif, Cody Wong
# HalfGone
# SoftDev
# P04 - Makers Makin' It, Act II -- The Seequel
# 2026-04-20
# time spent: 1

import sqlite3
import csv
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "data.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "static", "faang_stock_prices.csv")

SQL_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS stocks (
  id INTEGER PRIMARY KEY,
  ticker TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS stock_data (
  stock_id INTEGER NOT NULL,
  date TIMESTAMP NOT NULL,
  open_price FLOAT,
  close_price FLOAT,
  returns FLOAT,
  volume INTEGER,
  PRIMARY KEY (stock_id, date),
  FOREIGN KEY (stock_id) REFERENCES stocks(id)
);
"""

# Params:
    # ticker: stock id
    # limit: number of entries (eg. 30 = last 30 days)
# Returns: list of dicts, each containing stock data on a certain day
def get_stock_data_from_csv(ticker: str, limit: int = None) -> list[dict]:
    ticker = ticker.upper()
    results = []

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Ticker"].upper() == ticker:
                for col in (
                    "Open", "High", "Low", "Close", "Volume",
                    "SMA_7", "SMA_21", "EMA_12", "EMA_26",
                    "RSI_14", "MACD", "MACD_Signal",
                    "Bollinger_Upper", "Bollinger_Lower",
                    "Daily_Return", "Volatility_7d", "Next_Day_Close",
                ):
                    try:
                        row[col] = float(row[col]) if row[col] else None
                    except ValueError:
                        row[col] = None
                results.append(row)

    results.sort(key=lambda r: r["Date"], reverse=True)

    return results[:limit] if limit is not None else results

# Returns: list of all tickers in dataset
def get_all_tickers() -> list[str]:
    tickers = set()
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickers.add(row["Ticker"].upper())
    return sorted(tickers)

# Database population
def csv_populate(db: sqlite3.Connection):
    c = db.cursor()
    tickers = get_all_tickers()

    for ticker in tickers:
        c.execute(
            "INSERT OR IGNORE INTO stocks (ticker) VALUES (?)",
            (ticker,),
        )
        stock_id = c.execute(
            "SELECT id FROM stocks WHERE ticker = ?", (ticker,)
        ).fetchone()[0]

        rows = get_stock_data_from_csv(ticker)

        c.executemany(
            """
            INSERT OR IGNORE INTO stock_data
              (stock_id, date, open_price, close_price, returns, volume)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    stock_id,
                    row["Date"],
                    row["Open"],
                    row["Close"],
                    row["Daily_Return"],
                    int(row["Volume"]) if row["Volume"] is not None else None,
                )
                for row in rows
            ],
        )

    db.commit()

def main():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.executescript(SQL_SCHEMA)
    db.commit()
    has_stock_data = c.execute("SELECT COUNT(*) FROM stock_data").fetchone()[0] > 0
    if not has_stock_data:
        csv_populate(db)
    db.close()

if __name__ == "__main__":
    main()
