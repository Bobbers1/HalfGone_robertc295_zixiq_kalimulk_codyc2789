# Zixi Qiao, Robert Chen, Kalimul Kaif, Cody Wong
# HalfGone
# SoftDev
# P04 - Makers Makin' It, Act II -- The Seequel
# 2026-04-20
# time spent: 1

from flask import Flask, render_template, redirect, url_for, request, session

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
    return render_template("dashboard.html") # Reusing dashboard for basic skeleton

@app.route("/stock")
def stock():
    return render_template("stock_viewer.html")

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
