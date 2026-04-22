# FAANG+ Stock Explorer by HalfGone

# ROSTER:
Robert Chen - Project Manager <br>
Cody Wong - Backend Developer <br>
Zixi Qiao - Stock Analysis Features <br>
Kalimul Kaif - Visualizations <br>

# DESCRIPTION:
This project is an interactive stock exploration platform focused on major tech stocks and market leaders: AAPL, MSFT, AMZN, GOOGL, META, and NVDA. Users can register for an account and login to explore and compare these stocks through dynamic visualizations. The platform analyzes what differentiates these stocks in terms of growth over time, risk, and market behavior. Users can also compare FAANG+ stocks with other non-FAANG+ stocks they select. The dashboard displays indexed growth charts, risk vs return charts, and drawdown charts. An interactive exploration page allows users to select and compare stocks, while individual stock profiles provide detailed information.

# FEATURE SPOTLIGHT:
- Correlation matrix on the analysis page uses the pandas library to quantify how much different stock prices move together. Useful for traders in understanding how diversified their portfolio is 
  - In real life, these matrices would incorporate stocks across multiple sectors and not just the tech sector. As such, this is just a proof of concept for the scope of our project.
- Comparison feature on explore page is useful for analyzing how two companies' stock prices and trade volumes have fared and continue to fare against each other over the last five years. 
  - Data is updated live using the Yahoo Finance API and constantly changes during market open (from 9:30AM EST to 4PM EST on weekdays).
- Supply chain page presents a case study on three stocks (TSM, NVDA, TSLA) and their price drop/volume spike due to the release of DeepSeek's competitive AI model on January 27, 2025.

# LIVE SITE:
### Live Site: http://167.172.224.136
### Backup: http://104.131.173.65

# INSTALL GUIDE:
Pre-requisites:
- python3 installed
- git installed

Clone and enter repo:
```
$ git clone git@github.com:Bobbers1/HalfGone_robertc295_zixiq_kalimulk_codyc2789.git
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
$ cd app
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
