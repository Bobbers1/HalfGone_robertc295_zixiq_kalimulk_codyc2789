# Zixi Qiao, Robert Chen, Kalimul Kaif, Cody Wong
# HalfGone
# SoftDev
# P04 - Makers Makin' It, Act II -- The Seequel
# 2026-04-20
# time spent: 1

from flask import Flask, render_template, redirect, url_for, request, session
import urllib.request
import json
import yfinance as yf

app = Flask(__name__)
app.secret_key = 'half_gone'

@app.route("/")
def home():
    return redirect(url_for('login'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        # TODO: Add logic to hash password and insert into DB
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # TODO: Add logic to verify credentials
        session['user'] = request.form['username']
        return redirect(url_for('dashboard'))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("dashboard.html")

@app.route("/explore")
def explore():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("explore.html")

@app.route("/stock")
def stock():
    ticker = request.args.get('ticker')
    if not ticker:
        return redirect(url_for('dashboard'))

    data = yf.Ticker(ticker)
    hist = data.history(period="5y")

    dates = hist.index.strftime('%Y-%m-%d').tolist()
    closes = hist['Close'].round(2).tolist()

    return render_template("stock_viewer.html",
        ticker=ticker,
        dates=dates,
        closes=closes,
        latest_close=closes[-1],
        high=round(hist['High'].max(), 2),
        low=round(hist['Low'].min(), 2),
        avg_volume=f"{int(hist['Volume'].mean()):,}"
    )

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
