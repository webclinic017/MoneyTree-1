import sqlite3, config

if input("You're about to drop all tables in app.db. Are you sure? (y/n)") != "y":
    exit()

connection = sqlite3.connect(config.DB_FILE)
    
cursor = connection.cursor()

cursor.execute("""
    DROP TABLE stock_price
""")
cursor.execute("""
    DROP TABLE stock
""")

cursor.execute("""
    DROP TABLE stock_strategy
""")

cursor.execute("""
    DROP TABLE strategy
""")

cursor.execute("""
    DROP TABLE stock_price_minute
""")

cursor.execute("""
    DROP TABLE backtest_config
""")

cursor.execute("""
    DROP TABLE backtest_report
""")

connection.commit()