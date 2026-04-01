# Zixi Qiao, Robert Chen, Kalimul Kaif, Cody Wong
# HalfGone
# SoftDev
# P04 - Makers Makin' It, Act II -- THe Seequel
# 2026-04-20
# time spent: 1

from flask import Flask, render_template, redirect, url_for
app = Flask(__name__)           #create instance of class Flask
app.secret_key = 'half_gone'

@app.route("/", methods = ['GET', 'POST'])
def home():
    return "No tengo queso y manzanas! (Translation: \"I do not have cheese and apples!\")"

if __name__ == "__main__":      # true if this file NOT imported
    app.debug = True            # enable auto-reload upon code change
    app.run(host = '0.0.0.0', port = 5000)
