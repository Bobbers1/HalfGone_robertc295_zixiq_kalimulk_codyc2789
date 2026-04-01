# Zixi Qiao, Robert Chen, Kalimul Kaif, Cody Wong
# HalfGone
# SoftDev
# P04 - Makers Makin' It, Act II -- The Seequel
# 2026-04-20
# time spent: 1

import sqlite3

DB_FILE = "data.db"

SQL_SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS stocks;
DROP TABLE IF EXISTS stock_data;

CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE,
  password TEXT
);

CREATE TABLE stocks (
  id INTEGER PRIMARY KEY,
  ticker TEXT,
  company_name TEXT
);

CREATE TABLE stock_data (
  stock_id INTEGER,
  date TIMESTAMP,
  open_price FLOAT,
  close_price FLOAT,
  returns FLOAT,
  volume INTEGER,
  FOREIGN KEY(stock_id) REFERENCES stocks(id)
);
"""

def main():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.executescript(SQL_SCHEMA)
    db.commit()
    db.close()

if __name__ == "__main__":
    main()
