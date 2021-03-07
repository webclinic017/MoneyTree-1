import sys
sys.path.append("./")

import config
import alpaca_trade_api as tradeapi


api = tradeapi.REST(config.PAPER_API_KEY, config.PAPER_SECRET_KEY, base_url=config.PAPER_API_URL)

response = api.close_all_positions()

print(response)