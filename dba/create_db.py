import sys
sys.path.append("./")

import sqlite3, config

connection = sqlite3.connect(config.DB_FILE)

cursor = connection.cursor()

# creates the main stock table where we store all stock tickers
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY, 
        symbol TEXT NOT NULL UNIQUE, 
        name TEXT NOT NULL,
        exchange TEXT NOT NULL,
        shortable BOOLEAN NOT NULL,
        backtest_data BOOLEAN NOT NULL
    )
""")

# creates the stock_price table where we will store daily stock prices
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price (
        id INTEGER PRIMARY KEY, 
        stock_id INTEGER,
        date NOT NULL,
        open NOT NULL, 
        high NOT NULL, 
        low NOT NULL, 
        close NOT NULL, 
        volume NOT NULL,
        sma_20,
        sma_50,
        rsi_14,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price_minute (
        id INTEGER PRIMARY KEY,
        stock_id INTEGER,
        datetime NOT NULL,
        open NOT NULL,
        high NOT NULL,
        low NOT NULL,
        close NOT NULL,
        volume NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")

# insert into strategy table. (eventually build into MT app)
# INSERT INTO strategy (name) values (<new strategy name>);

# creates the strategy table where we will store our different strategies
cursor.execute("""
    CREATE TABLE IF NOT EXISTS strategy (
        id INTEGER PRIMARY KEY,
        name NOT NULL
    ) 
""")

# creates the stock_strategy table where we will store our stocks and the
#  strategy that we applied to that stock
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_strategy (
        stock_id INTEGER NOT NULL,
        strategy_id INTEGER NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
        FOREIGN KEY (strategy_id) REFERENCES strategy (id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS backtest_config (
        run_id INTEGER PRIMARY KEY,
        date NOT NULL,
        stock_id INTEGER,
        strategy NOT NULL,
        bt_start NOT NULL,
        bt_end NOT NULL,
        set_cash INTEGER NOT NULL,
        open_range INTEGER NOT NULL,
        liquidate_time INTEGER NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS backtest_report (
        run_id INTEGER,
        start_cash INTEGER,
        rpl REAL,
        result_won_trades REAL,
        result_lost_trades REAL,
        profit_factor REAL,
        rpl_per_trade REAL,
        total_return REAL,
        annual_return REAL,
        max_money_drawdown REAL,
        max_pct_drawdown REAL,
        total_number_trades INTEGER,
        trades_closed INTEGER,
        pct_winning REAL,
        pct_losing REAL,
        avg_money_winning REAL,
        avg_money_losing REAL,
        best_winning_trade REAL,
        worst_losing_trade REAL,
        sharpe_ratio REAL,
        sqn_score REAL,
        sqn_human TEXT,
        FOREIGN KEY(run_id) REFERENCES backtest_config(run_id)
    )
""")

# inserts strategies into the strategy table
strategies = ['opening_range_breakout', 'opening_range_breakdown','bollinger_bands']

for strategy in strategies:
    cursor.execute("""
        INSERT INTO strategy (name) VALUES (?)
    """, (strategy,))

connection.commit()