from tda import auth, client
from tda.orders.common import OrderType, Duration, Session
from tda.orders.generic import OrderBuilder
from tda.orders.equities import equity_buy_limit
import json, config

try:
    c = auth.client_from_token_file(config.tda_token_path, config.tda_api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path='/Users/kylespringfield/Dev/MoneyTree/chromedriver') as driver:
        c = auth.client_from_login_flow(
            driver, config.tda_api_key, config.tda_redirect_uri, config.tda_token_path)

# r = c.get_price_history('AAPL',
#         period_type=client.Client.PriceHistory.PeriodType.YEAR,
#         period=client.Client.PriceHistory.Period.TWENTY_YEARS,
#         frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
#         frequency=client.Client.PriceHistory.Frequency.DAILY)
# assert r.status_code == 200, r.raise_for_status()
# print(json.dumps(r.json(), indent=4))

# # Get quotes
# res = c.get_quotes('AAPL')

# print(json.dumps(res.json(), indent=4))

# # Get Fundamentals
# res = c.search_instruments(['AAPL'], c.Instrument.Projection.FUNDAMENTAL)

# print(json.dumps(res.json(), indent=4))

# # Get movers
res = c.get_movers(index='SPX.X', direction=c.Movers.Direction.UP, change=c.Movers.Change.PERCENT)

print(json.dumps(res.json(), indent=4))


# # Options
# print(json.dumps(res.json(), indent=4))

# res = c.get_option_chain('AAPL')

# print(json.dumps(res.json(), indent=4))

# res = c.get_option_chain('AAPL', contract_type=c.Options.ContractType.CALL,
#                          strike=120)

# print(json.dumps(res.json(), indent=4))

# # Account Info
# res = c.get_account(config.tda_account_id)

# print(json.dumps(res.json(), indent=4))


