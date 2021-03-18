import sys
sys.path.append("/Users/kylespringfield/Dev/MoneyTree/")

from tda.auth import easy_client
from tda.client import Client
from tda.streaming import StreamClient

import asyncio
import json
import config, sqlite3
import time
import datetime
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO, filename='/Users/kylespringfield/Dev/MoneyTree/logs/tda_stream.log')

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

# Delete all from tda_stock_price_minute table. Do not need to store this info. Also will prevent dups.
cursor.execute("""
    DELETE FROM tda_stock_price_minute
""")
connection.commit()

cursor.execute("""
    SELECT symbol, name
    FROM stock
    JOIN stock_strategy ON stock_strategy.stock_id = stock.id
""")

stocks = cursor.fetchall()
symbols = [stock['symbol'] for stock in stocks]
logging.info(symbols)

client = easy_client(
        api_key=config.tda_api_key,
        redirect_uri=config.tda_redirect_uri,
        token_path=config.tda_token_path)

stream_client = StreamClient(client, account_id=config.tda_account_id)

async def insert_stream_data(msg, symbols):
        data = json.loads(msg)

        with sqlite3.connect(config.DB_FILE) as conn:
                conn.execute(
                """CREATE TABLE IF NOT EXISTS tda_stock_price_minute (
                        seq INTEGER,
                        key TEXT,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume INTEGER,
                        sequence INTEGER,
                        chart_time BLOB,
                        chart_day BLOB
                        );"""
                )

                # Insert each entry from json into the table.
                keys = ["seq", "key", "OPEN_PRICE", "HIGH_PRICE", "LOW_PRICE", "CLOSE_PRICE", "VOLUME", "SEQUENCE", "CHART_TIME", "CHART_DAY"]
                for entry in data:

                        entry["CHART_TIME"] = datetime.datetime.fromtimestamp(entry["CHART_TIME"]/1000.0)
                        entry["CHART_TIME"] = entry["CHART_TIME"].strftime('%Y-%m-%d %H:%M:%S')

                        # This will make sure that each key will default to None
                        # if the key doesn't exist in the json entry.
                        values = [entry.get(key, None) for key in keys]

                        # Execute the command and replace '?' with the each value
                        # in 'values'. DO NOT build a string and replace manually.
                        # the sqlite3 library will handle non safe strings by doing this.
                        cmd = """INSERT INTO tda_stock_price_minute VALUES(
                                ?,
                                ?,
                                ?,
                                ?,
                                ?,
                                ?,
                                ?,
                                ?,
                                ?,
                                ?
                                );"""
                        conn.execute(cmd, values)
                
                conn.commit()

                now = time.time()
                now = datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
        
        return logging.info(f"inserted new prices for {symbols}")

async def read_stream(symbol, symbols):
        await stream_client.login()
        await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

        # Always add handlers before subscribing because many streams start sending
        # data immediately after success, and messages with no handlers are dropped.
        stream_client.add_chart_equity_handler(
                # lambda msg: print(json.dumps(msg['content'], indent=4)))
                lambda msg: insert_stream_data(json.dumps(msg['content'], indent=4), symbols))

        await stream_client.chart_equity_subs([symbols[0]])

        for s in symbols:
                await stream_client.chart_equity_add([s])

        # set to run from 9am - 4pm
        stream_end = time.time() + 60 * 420

        st = datetime.datetime.fromtimestamp(stream_end).strftime('%Y-%m-%d %H:%M:%S')

        logging.info(f"stream end: {st}")

        while time.time() < stream_end:
                await stream_client.handle_message()

asyncio.run(read_stream(symbols[0], symbols))