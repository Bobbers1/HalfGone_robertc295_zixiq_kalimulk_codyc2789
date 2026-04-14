# Zixi Qiao, Robert Chen, Kalimul Kaif, Cody Wong
# HalfGone
# SoftDev
# P04 - Makers Makin' It, Act II -- The Seequel
# 2026-04-20
# time spent: 1

import sqlite3
DB_FILE = "data.db"

SQL_SCHEMA = """
DROP TABLE IF EXISTS stock_data;
DROP TABLE IF EXISTS stocks;
DROP TABLE IF EXISTS users;

PRAGMA foreign_keys = ON;

CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stocks (
  id INTEGER PRIMARY KEY,
  ticker TEXT UNIQUE NOT NULL,
  company_name TEXT NOT NULL
);

CREATE TABLE stock_data (
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

def main():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.executescript(SQL_SCHEMA)
    db.commit()
    db.close()

if __name__ == "__main__":
    main()
