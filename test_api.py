import alpaca_trade_api as tradeapi
import config, notifications

api = tradeapi.REST(config.PAPER_API_KEY, config.PAPER_SECRET_KEY, base_url=config.PAPER_API_URL)
account = api.get_account()
print(account.status)

assets = api.list_assets()
print(assets)

messages = []
short_messages = []
messages.append(f"TEST TEST")
short_messages.append(f"TEST TEST")
strategy_name = 'Test'
# notifications.send_trade_notification(messages,short_messages,strategy_name)