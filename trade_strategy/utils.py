import math
import pandas as pd
from dateutil import parser
from datetime import datetime
import pytz

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

def is_dst():
    """Determine whether or not Daylight Savings Time (DST)
    is currently in effect"""

    x = datetime(datetime.now().year, 1, 1, 0, 0, 0, tzinfo=pytz.timezone('US/Eastern'))
    y = datetime.now(pytz.timezone('US/Eastern'))

    return not (y.utcoffset() == x.utcoffset())