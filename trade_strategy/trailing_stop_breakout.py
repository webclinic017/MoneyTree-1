import config, tulipy
import alpaca_trade_api as tradeapi
from utils import calculate_quantity
from datetime import date, datetime
import datetime as dt
import pytz

print(datetime.now())

strategy = 'trailing_stop_breakout'
print(strategy)

# connection = sqlite3.connect(config.DB_FILE)
# connection.row_factory = sqlite3.Row

# cursor = connection.cursor()

# cursor.execute("""
#     SELECT id FROM strategy WHERE name = ?
# """, (strategy_name,))

# strategy_id = cursor.fetchone()['id']

# cursor.execute("""
#     SELECT symbol, name
#     FROM stock
#     JOIN stock_strategy ON stock_strategy.stock_id = stock.id
#     WHERE stock_strategy.strategy_id = ?
# """, (strategy_id,))

# stocks = cursor.fetchall()
# symbols = [stock['symbol'] for stock in stocks]
symbols = ['SPY']

api = tradeapi.REST(config.PAPER_API_KEY, config.PAPER_SECRET_KEY, base_url=config.PAPER_API_URL)

current_date = date.today().isoformat()
four_months_ago_date = (date.today() - dt.timedelta(days=120)).isoformat()
print(four_months_ago_date)

portfolio = api.list_positions()
orders = api.list_orders()
existing_order_symbols = [order.symbol for order in orders if order.status != 'canceled']

# Trailing Stop Breakout

# Ideas
# Trailing Stop Breakout
#  Uses a combination of % change in upwards price and volume over the past 10 minute bars
#  to determine if a stock is breaking out. If so, the stock is bought
#  and then once filled a trailing stop percent order will be applied.

# end = pytz.timezone('America/New_York').localize(datetime.now()).timestamp()*1000
end = pytz.timezone('America/New_York').localize(datetime(2021,2,25,10,0)).timestamp()*1000
print(end)

# start = datetime.now() - dt.timedelta(minutes=10)
start = datetime(2021,2,25,10,0) - dt.timedelta(minutes=10)
start = pytz.timezone('America/New_York').localize(start).timestamp()*1000
print(start)

for symbol in symbols:

    daily_bars = api.polygon.historic_agg_v2(symbol, 1, 'minute', _from=start, to=end).df
    print(daily_bars)

    # atr = tulipy.atr(daily_bars.high.values, daily_bars.low.values, daily_bars.close.values, 14)

    # print(atr)

    # trailing stop percent
    # for position in portfolio:
    #     print(f"{position.symbol}, {position.qty}")

    #     if position.symbol not in existing_order_symbols:




    # symbols = ['SPY', 'IWM', 'DIA']

    # for symbol in symbols:
    #     quote = api.get_last_quote(symbol)

    #     qty = calculate_quantity(quote.bidprice)

    #     api.submit_order(
    #         symbol=symbol,
    #         side='buy',
    #         type='market',
    #         qty=qty
    #         time_in_force='day'
    #     )


    # orders = api.list_orders()
    # print(orders)

    # # trail percent order
    # ap.submit_order(
    #     symbol=symbol,
    #     side='sell',
    #     qty=qty,
    #     time_in_force='day',
    #     type='trailing_stop',
    #     trail_percent='0.70'
    # )