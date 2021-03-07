import sys
sys.path.append("./")

import sqlite3, config
import alpaca_trade_api as tradeapi
from datetime import date

print(date.today().isoformat())

# connect to app.db
connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

# selects symbol, name columns from stock db
cursor.execute("""SELECT symbol, name FROM stock""")

# creates an interable list of lists
rows = cursor.fetchall()

# creates a list of symbols that we currently have in stock db
symbols = [row['symbol'] for row in rows]

# api variables
api = tradeapi.REST(config.PAPER_API_KEY, config.PAPER_SECRET_KEY, config.PAPER_API_URL)
assets = api.list_assets()

for asset in assets:
    try:
        if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:
            print(f"Added a new stock {asset.symbol} {asset.name}")
            cursor.execute("INSERT INTO stock (symbol, name, exchange, shortable) VALUES (?,?,?,?)", (asset.symbol, asset.name, asset.exchange, asset.shortable))
    except Exception as e:
        print(asset.symbol)
        print(e)

connection.commit()