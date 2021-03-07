import sys
sys.path.append("./")

import sqlite3, config, datetime
import alpaca_trade_api as tradeapi
from datetime import date
import tulipy, numpy

current_date = date.today().isoformat()
print(current_date)

# storing 90 days worth of daily price data
d = datetime.timedelta(days=120)
from_date = (datetime.datetime.now() - d).isoformat()
print(from_date)

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
cursor.execute("""SELECT id, symbol, name FROM stock""")

rows = cursor.fetchall()
symbols = []
stock_dict = {}

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL) 

for row in rows:
    symbol = row['symbol']
    stock_id = row['id']

    barset = api.polygon.historic_agg_v2(symbol, 1, 'day', _from=from_date, to=current_date)

    print(f"processing symbol {symbol}")

    recent_closes = [bar.close for bar in barset]

    for bar in barset:

        if len(recent_closes) >= 50 and current_date == bar.timestamp.date().isoformat():
            sma_20 = tulipy.sma(numpy.array(recent_closes), period=20)[-1]
            sma_50 = tulipy.sma(numpy.array(recent_closes), period=50)[-1]
            rsi_14 = tulipy.rsi(numpy.array(recent_closes), period=14)[-1]
        else:
            sma_20, sma_50, rsi_14 = None, None, None

        cursor.execute("""
            INSERT INTO stock_price (stock_id, date, open, high, low, close, volume, sma_20, sma_50, rsi_14)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (stock_id, bar.timestamp.date(), bar.open, bar.high, bar.low, bar.close, bar.volume, sma_20, sma_50, rsi_14))

connection.commit()