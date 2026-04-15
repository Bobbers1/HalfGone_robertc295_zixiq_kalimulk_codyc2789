# FAANG+ Stock Explorer by HalfGone

# ROSTER:
Robert Chen - Project Manager <br>
Cody Wong - Backend Developer <br>
Zixi Qiao - Stock Analysis Features <br>
Kalimul Kaif - Visualizations <br>

# DESCRIPTION:
This project is an interactive stock exploration platform focused on major tech stocks and market leaders: AAPL, MSFT, AMZN, GOOGL, META, and NVDA. Users can register for an account and login to explore and compare these stocks through dynamic visualizations. The platform analyzes what differentiates these stocks in terms of growth over time, risk, and market behavior. Users can also compare FAANG+ stocks with other non-FAANG+ stocks they select. The dashboard displays indexed growth charts, risk vs return charts, and drawdown charts. An interactive exploration page allows users to select and compare stocks, while individual stock profiles provide detailed information.

### Site: http://192.168.1.231:5000
# INSTALL GUIDE:
Pre-requisites:
- python3 installed
- git installed

Clone and enter repo:
```
$ git clone git@github.com:stuy-softdev/lost-duckies__codyw2789_hannahg61_sarahz40_stevenw92.git
cd lost-duckies__codyw2789_hannahg61_sarahz40_stevenw92/
```

Create virtual environment:
```
python -m venv venv_name
```

Enter virtual environment 
(macOs & Linux):
```
source venv_name/bin/activate
```
(Windows):
```
venv_name\Scripts\activate
```

Install packages and libraries:
```
$ pip install -r requirements.txt
```

# LAUNCH CODES:
From directory of where repo is stored

Enter "app" section of repo:
```
$ cd lost-duckies__codyw2789_hannahg61_sarahz40_stevenw92/app
```

Initialize database (this might be removed later on...):
```
python build_db.py
```

Run app:
```
$ python __init__.py
```

Open the Flask host webpage on browser:
```
http://127.0.0.1:5000
```

(To quit, open your terminal page and press ```CTRL + C``` to quit the site program)
