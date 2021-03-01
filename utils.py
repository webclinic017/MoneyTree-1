import math
import pandas as pd
from dateutil import parser

def calculate_quantity(price):

    quantity = math.floor(10000 / price)

    return quantity

def get_market_hours_time():
    market_hours_time = []
    market_hours = pd.date_range("09:30", "16:00", freq="1min").strftime('%H:%M:%S')

    for m in market_hours:
        mt = parser.parse(m)
        market_hours_time.append(mt.time())

    return market_hours_time