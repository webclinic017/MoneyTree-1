import sqlite3, config, datetime, calendar, os
import alpaca_trade_api as tradeapi
from fastapi import FastAPI, Request, Form
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import date
from flask import send_from_directory
from utils import get_market_hours_time, timestamp2date
from typing import List
from datetime import datetime as dt
import pandas as pd
from pydantic import BaseModel
from backtesting.backtest import backtest, saveplots

from babel.numbers import format_currency

from flask import Flask
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def init_app():
    """Construct core Flask application with embedded Dash app."""
    dapp = Flask(__name__, instance_relative_config=False)
    # dapp.config.from_object('config.Config')

    with dapp.app_context():

        from backtesting.dashboard import init_dashboard
        dapp = init_dashboard(dapp)

        print(f'== dapp initialized: {dapp} ==')

        return dapp

# decorator that provides the route on the local host
@app.get("/")
def index(request: Request):
    stock_filter = request.query_params.get('filter', False)

    # connect to app.db
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT MAX(date) FROM stock_price
    """)
    row = cursor.fetchone()
    date_fil = row[0]

    if stock_filter == 'new_closing_highs':
        cursor.execute("""
        SELECT * FROM (
            SELECT symbol, name, stock_id, max(close), date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            GROUP BY stock_id
            ORDER BY symbol
        ) WHERE date = ?
        """, (date_fil,))
    elif stock_filter == 'new_closing_lows':
        cursor.execute("""
        SELECT * FROM (
            SELECT symbol, name, stock_id, min(close), date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            GROUP BY stock_id
            ORDER BY symbol
        ) WHERE date = ?
        """, (date_fil,))
    elif stock_filter == 'rsi_overbought':
        cursor.execute("""
            SELECT symbol, name, stock_id, date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            WHERE rsi_14 > 70
            AND date = (select max(date) from stock_price)
            ORDER BY symbol
        """)
    elif stock_filter == 'rsi_oversold':
        cursor.execute("""
            SELECT symbol, name, stock_id, date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            WHERE rsi_14 < 30
            AND date = (select max(date) from stock_price)
            ORDER BY symbol
        """)
    elif stock_filter == 'above_sma_20':
        cursor.execute("""
            SELECT symbol, name, stock_id, date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            WHERE close > sma_20
            AND date = (select max(date) from stock_price)
            ORDER BY symbol
        """)
    elif stock_filter == 'below_sma_20':
        cursor.execute("""
            SELECT symbol, name, stock_id, date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            WHERE close < sma_20
            AND date = (select max(date) from stock_price)
            ORDER BY symbol
        """)
    elif stock_filter == 'above_sma_50':
        cursor.execute("""
            SELECT symbol, name, stock_id, date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            WHERE close > sma_50
            AND date = (select max(date) from stock_price)
            ORDER BY symbol
        """)
    elif stock_filter == 'below_sma_50':
        cursor.execute("""
            SELECT symbol, name, stock_id, date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            WHERE close < sma_50
            AND date = (select max(date) from stock_price)
            ORDER BY symbol
        """)
    else:
        # selects symbol, name columns from stock db
        stock_filter = 'all_stocks'
        cursor.execute("""
            SELECT id, symbol, name FROM stock ORDER BY symbol
        """)

    # header reformat dict
    sf_reformat = {"all_stocks": "All Stocks",
                   "new_closing_highs": "New Closing Highs",
                   "new_closing_lows": "New Closing Lows",
                   "rsi_overbought": "RSI Overbought",
                   "rsi_oversold": "RSI Oversold",
                   "above_sma_20": "Above SMA 20",
                   "below_sma_20": "Below SMA 20",
                   "above_sma_50": "Above SMA 50",
                   "below_sma_50": "Above SMA 50"}


    # creates an interable list of lists
    rows = cursor.fetchall()

    cursor.execute("""
        SELECT symbol, rsi_14, sma_20, sma_50, close
        FROM stock JOIN stock_price on stock_price.stock_id = stock.id
        WHERE date = ?
    """, (date_fil,))

    indicator_rows = cursor.fetchall()
    indicator_values = {}

    for row in indicator_rows:
        indicator_values[row['symbol']] = row

    print(indicator_values)

    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "selection": sf_reformat[stock_filter], "date": date_fil, "indicator_values": indicator_values})

@app.get("/stock/{symbol}")
def stock_detail(request: Request, symbol):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM strategy
    """)
    
    strategies = cursor.fetchall()

    # selects symbol, name columns from stock db
    cursor.execute("""
        SELECT id, symbol, name FROM stock WHERE symbol = ?
    """, (symbol,))

    # creates an interable list of lists
    row = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM stock_price WHERE stock_id = ? ORDER BY date DESC
    """, (row['id'],))

    prices = cursor.fetchall()

    return templates.TemplateResponse("stock_detail.html", {"request": request, "stock": row, "bars": prices, "strategies": strategies})

# post request for processing a form. inserting data into the database
@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), stock_id: int = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (?,?)
    """, (stock_id, strategy_id))
    
    connection.commit()

    return RedirectResponse(url=f"/strategy/{strategy_id}", status_code=303)

@app.get("/strategies")
def strategies(request: Request):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM strategy
    """)

    strategies = cursor.fetchall()

    return templates.TemplateResponse("strategies.html", {"request": request, "strategies": strategies})

@app.get("/orders")
def orders(request: Request):

    api = tradeapi.REST(config.PAPER_API_KEY, config.PAPER_SECRET_KEY, base_url=config.PAPER_API_URL)

    orders = api.list_orders(status='all')

    return templates.TemplateResponse("orders.html", {"request": request, "orders": orders})

@app.get("/strategy/{strategy_id}")
def strategy(request: Request, strategy_id):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name
        FROM strategy
        WHERE id = ?
    """, (strategy_id,))

    strategy = cursor.fetchone()

    cursor.execute("""
        SELECT symbol, name
        FROM stock JOIN stock_strategy on stock_strategy.stock_id = stock.id
        WHERE strategy_id = ?
    """, (strategy_id,))

    stocks = cursor.fetchall()

    return templates.TemplateResponse("strategy.html", {"request": request, "stocks": stocks, "strategy": strategy})

@app.get("/backtesting")
def backtest_start(request: Request):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    #setting static start and end dates for now
    sdate = dt(2020, 4, 13).date()
    edate = dt(2021, 2, 19).date()
    dates = pd.date_range(sdate,edate-datetime.timedelta(days=1),freq='d')

    cursor.execute("""
        SELECT * FROM stock
        WHERE backtest_data = 1
    """)
    
    stocks = cursor.fetchall()

    opening_range = list(range(1,60))

    liquidate_time = get_market_hours_time()

    set_cash = list(range(20000,100001, 5000))

    strategies = ['opening_range_breakout','crossover']

    return templates.TemplateResponse("backtest_start.html", {"request": request, "stocks": stocks, "opening_range": opening_range, \
                                                           "liquidate_time":liquidate_time, "set_cash":set_cash, "strategies":strategies, \
                                                           "dates":dates})

@app.post("/submit_backtest_config", status_code=201)
def submit_backtest_config(stock_id: int = Form(...), start_date: str = Form(...), end_date: str = Form(...), \
                           strategy: str = Form(...), set_cash: int = Form(...), open_range: int = Form(...), \
                           liquidate_time: str = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT MAX(run_id)
    FROM backtest_config
    """)

    max_run_id = cursor.fetchone()

    try:
        run_id = max_run_id[0]+1
    except TypeError:
        run_id = 1

    date = dt.now()

    bt_start = start_date

    bt_end = end_date

    cursor.execute("""
        INSERT INTO backtest_config (run_id, date, stock_id, strategy, bt_start, bt_end, set_cash, open_range, liquidate_time) VALUES (?,?,?,?,?,?,?,?,?)
    """, (run_id, date, stock_id, strategy, bt_start , \
          bt_end, set_cash, open_range, liquidate_time))
    
    connection.commit()

    return RedirectResponse(url=f"/backtesting/config_set_{stock_id}", status_code=303)

@app.get("/backtesting/config_set_{stock_id}")
def backtest_config_set(request: Request, stock_id):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT symbol, name
        FROM stock
        WHERE id = ?
    """, (stock_id,))

    stock = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM backtest_config
        WHERE stock_id = ?
        ORDER BY date DESC
    """, (stock_id,))

    backtest_configs = cursor.fetchall()

    set_config = backtest_configs[0]

    print(set_config)

    return templates.TemplateResponse("backtest_config_set.html", {"request":request, "stock":stock, \
                                                                   "backtest_configs":backtest_configs, \
                                                                   "set_config":set_config})

# post for running the backtest. the redirect will go to the performance report page
@app.post("/run_backtest", status_code=201)
async def run_backtest(stock_id: int = Form(...), run_id: int = Form(...)):
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM backtest_config
    WHERE run_id = ?
    """, (run_id,))

    bt_config = cursor.fetchone()

    backtest(stock_id=bt_config['stock_id'], strategy=bt_config['strategy'], conn=conn,
             start_date=bt_config['bt_start'], end_date=bt_config['bt_end'], open_range=bt_config['open_range'],
             run_id=bt_config['run_id'], liquidate_time=bt_config['liquidate_time'], set_cash=bt_config['set_cash'])

    return RedirectResponse(url=f"/backtesting/final_report_{stock_id}_{run_id}", status_code=303)

@app.get("/backtesting/final_report_{stock_id}_{run_id}")
def final_report(request: Request, stock_id, run_id):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT symbol, name
        FROM stock
        WHERE id = ?
    """, (stock_id,))

    stock = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM backtest_report
        WHERE run_id = ?
    """, (run_id,))

    report = cursor.fetchone()

    cursor.execute("""
    SELECT *
    FROM backtest_config
    WHERE run_id = ?
    """, (run_id,))

    bt_config = cursor.fetchone()

    dapp = init_app()
    app.mount("/", WSGIMiddleware(dapp))

    return templates.TemplateResponse("backtest_final_report.html", {"request":request, "stock":stock, \
                                                                     "report":report, "config":bt_config})

if __name__ == "__main__":
    uvicorn.run(app)