import sqlite3, config, notifications, ssl
import alpaca_trade_api as tradeapi
from datetime import date, datetime
from timezone import is_dst

print(datetime.now())

# Opening Range Break Strategy
strategy_name = 'opening_range_breakout'

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
    end_minute_bar = f"{current_date} 09:45:00-05:00"
else:
    start_minute_bar = f"{current_date} 09:30:00-04:00"
    end_minute_bar = f"{current_date} 09:45:00-04:00"

orders = api.list_orders(status='all', after=current_date)
existing_order_symbols = [order.symbol for order in orders if order.status != 'canceled']
print(existing_order_symbols)

messages = []
short_messages = []

qty = 100

for symbol in symbols:
    
    minute_bars = api.polygon.historic_agg_v2(symbol, 1, 'minute', _from=current_date, to=current_date).df
    
    opening_range_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]

    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].max()
    opening_range = opening_range_high - opening_range_low

    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]

    after_opening_range_breakout = after_opening_range_bars[after_opening_range_bars['close'] > opening_range_high]

    if not after_opening_range_breakout.empty:
        if symbol not in existing_order_symbols:
            
            limit_price = after_opening_range_breakout.iloc[0]['close']

            total_spend = qty * limit_price
            total_profit = qty * (limit_price + opening_range) - (qty * limit_price)
            total_loss = abs(qty * (limit_price - opening_range) - (qty * limit_price))

            messages.append(f"BUY >>>>>>> {symbol}")
            messages.append(f"Total Spend: ${total_spend} @ ${limit_price} per share")
            messages.append(f"Total Potential Profit: +${round(total_profit,0)} @ ${round((limit_price + opening_range),2)} per share")
            messages.append(f"Total Potential Loss: -${round(total_loss,0)} @ ${round((limit_price - opening_range),2)} per share")
            messages.append(f"1 Min Bar closed above {opening_range_high}:")
            messages.append(f"{after_opening_range_breakout.iloc[0]}\n\n")

            short_messages.append(f"B | {symbol} | ${round(limit_price,2)} | ${round(total_spend,2)} | +${round(total_profit,2)} | -${round(total_loss,2)} ")
            print(f"placing order for {symbol} at {limit_price}, closed_above {opening_range_high} at {after_opening_range_breakout.iloc[0]}")

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
                        limit_price=limit_price + opening_range,
                    ),
                    stop_loss=dict(
                        stop_price=limit_price - opening_range,
                    )
                )
            except Exception as e:
                print(f"could not submit order; {e}")

        else:
            print(f"Already an order for {symbol}, skipping")

# send email notification
print(short_messages)
notifications.send_trade_notification(messages,short_messages,strategy_name)