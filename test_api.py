import alpaca_trade_api as tradeapi
import config

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)
account = api.get_account()
print(account.status)

assets = api.list_assets()
print(assets)