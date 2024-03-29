import sys
sys.path.append("/Users/kylespringfield/Dev/MoneyTree/")

import sqlite3, config, notifications, ssl, tulipy
import alpaca_trade_api as tradeapi
from datetime import date, datetime
from utils import calculate_quantity, is_dst
import pandas as pd

conn = sqlite3.connect(config.DB_FILE)

# removed the limit of 1 because I forgot that the replacement df is a historical minute by minute price history for the current day.
def get_latest_tda_minute_bars(symbol, conn):
    df = pd.read_sql("""
        SELECT *
        FROM tda_stock_price_minute
        WHERE key = :symbol
        ORDER BY chart_time DESC
    """, conn, params={"symbol":symbol})

    return df

print(datetime.now())
 
# Eventually refactor into a Strategy class
# Opening Range Break Strategy
strategy_name = 'bollinger_bands'
print(strategy_name)

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id FROM strategy WHERE name = ?
""", (strategy_name,))

strategy_id = cursor.fetchone()['id']

cursor.execute("""
    SELECT symbol, name
    FROM stock
    JOIN stock_strategy ON stock_strategy.stock_id = stock.id
    WHERE stock_strategy.strategy_id = ?
""", (strategy_id,))

stocks = cursor.fetchall()
symbols = [stock['symbol'] for stock in stocks]

api = tradeapi.REST(config.PAPER_API_KEY, config.PAPER_SECRET_KEY, base_url=config.PAPER_API_URL)

current_date = date.today().isoformat()

if is_dst():
    start_minute_bar = f"{current_date} 09:30:00-05:00"
    end_minute_bar = f"{current_date} 16:00:00-05:00"
else:
    start_minute_bar = f"{current_date} 09:30:00-04:00"
    end_minute_bar = f"{current_date} 16:00:00-04:00"

orders = api.list_orders(status='all', after=current_date)
existing_order_symbols = [order.symbol for order in orders if order.status != 'canceled']
print(existing_order_symbols)

messages = []
short_messages = []

for symbol in symbols:

    # REPLACE with tda-stream
    # minute_bars = api.polygon.historic_agg_v2(symbol, 1, 'minute', _from=current_date, to=current_date).df

    # REPLACEMENT
    minute_bars = get_latest_tda_minute_bars(symbol, conn)

    market_open_mask = (minute_bars.chart_time >= start_minute_bar) & (minute_bars.chart_time < end_minute_bar)
    market_open_bars = minute_bars.loc[market_open_mask]

    if len(market_open_bars) >= 20:
        closes = market_open_bars.close.values
        
        lower, middle, upper = tulipy.bbands(closes, 20, 2)

        current_candle = market_open_bars.iloc[-1]
        previous_candle = market_open_bars.iloc[-2]

        # entry signal
        if current_candle.close > lower[-1] and previous_candle.close < lower[-2]:
            
            if symbol not in existing_order_symbols:

                limit_price = current_candle.close
                candle_range = current_candle.high - current_candle.low

                qty = calculate_quantity(limit_price)
                print(f"placing order for {symbol} at {limit_price}")

                total_spend = qty * limit_price
                total_profit = (qty * (limit_price + (candle_range * 3))) - (qty * limit_price)
                total_loss = abs(qty * (previous_candle.low) - (qty * limit_price))

                messages.append(f"BUY >>>>>>> {symbol}")
                messages.append(f"Total Spend: ${total_spend} @ ${limit_price} per share")
                messages.append(f"Total Potential Profit: +${round(total_profit,0)} @ ${round((limit_price + (candle_range * 3)),2)} per share")
                messages.append(f"Total Potential Loss: -${round(total_loss,0)} @ ${round(previous_candle.low,2)} per share")
                messages.append(f"Bollinger Band entry signal:")
                messages.append(f"current_close: {current_candle.close} > lower_Bband: {lower[-1]} AND")
                messages.append(f"previous_close: {previous_candle.close} < previous_lower_Bband: {lower[-2]}") 
                messages.append(f"{current_candle}\n\n")

                short_messages.append(f"B | {symbol} | ${round(limit_price,2)} | ${round(total_spend,2)} | +${round(total_profit,2)} | -${round(total_loss,2)} ")

                try:
                    api.submit_order(
                        symbol=symbol,
                        side='buy',
                        type='limit',
                        qty= qty,
                        time_in_force='day',
                        order_class='bracket',
                        limit_price=limit_price,
                        take_profit=dict(
                            limit_price=limit_price + (candle_range * 3),
                        ),
                        stop_loss=dict(
                            stop_price=previous_candle.low,
                        )
                    )
                except Exception as e:
                    print(f"could not submit order; {e}")
                    
            else:
                print(f"Already an order for {symbol}, skipping")

# send email notification
print(short_messages)
notifications.send_trade_notification(messages,short_messages,strategy_name)