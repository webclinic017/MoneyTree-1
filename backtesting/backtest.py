# -*- coding: utf-8; py-indent-offset:4 -*-
import os, sqlite3, config, sys
import pandas as pd
import backtrader as bt
from backtesting.report import Cerebro
from strategy_classes import CrossOver, OpeningRangeBreakout

# Convert this into a bactest function that can be called within main and it runs and inserts 
#  data into the database. The inserting into the database part can be done within the report.py file.

# The adjacent get function will pull the data from the database using the run_id.
#  The data will then be presented.

def saveplots(cerebro, numfigs=1, iplot=True, start=None, end=None,
             width=16, height=9, dpi=300, tight=True, use=None, file_path = '', **kwargs):

        from backtrader import plot
        if cerebro.p.oldsync:
            plotter = plot.Plot_OldSync(**kwargs)
        else:
            plotter = plot.Plot(**kwargs)

        figs = []
        for stratlist in cerebro.runstrats:
            for si, strat in enumerate(stratlist):
                rfig = plotter.plot(strat, figid=si * 100,
                                    numfigs=numfigs, iplot=iplot,
                                    start=start, end=end, use=use)
                figs.append(rfig)

        for fig in figs:
            for f in fig:
                f.savefig(file_path, bbox_inches='tight')
        return figs

def backtest(stock_id, strategy, conn, start_date=None, end_date=None, \
             open_range=None, run_id=None,liquidate_time='15:00:00', set_cash=25000):
    
    print(f"== Testing {stock_id} ==")
    
    df = pd.read_sql("""
        SELECT datetime, open, high, low, close, volume
        FROM stock_price_minute
        WHERE stock_id = :stock_id
        AND strftime('%Y-%m-%d', datetime) >= :start_date
        AND strftime('%Y-%m-%d', datetime) <= :end_date
        ORDER BY datetime ASC
        """, conn, params={"stock_id":stock_id,"start_date":start_date, \
                           "end_date":end_date}, index_col='datetime', parse_dates=['datetime'])
    data = df.between_time('09:30:00', '16:00:00')
    
    # initialize Cerebro engine, extende with report method
    cerebro = Cerebro()
    cerebro.broker.setcash(set_cash)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
    
    # add data
    feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(feed)
    
    if strategy == 'opening_range_breakout':
        cerebro.addstrategy(strategy=OpeningRangeBreakout)
    else:
        # add Golden Cross strategy
        params = (('fast', 50),('slow', 200))
        cerebro.addstrategy(strategy=CrossOver, **dict(params))
        
    cerebro.run()
    
    # saveplots(cerebro, file_path = 'backtest_output.png')
    
    cerebro.report(conn, memo=f'{stock_id} | {run_id}', run_id=run_id)
    
    return print('== Backtesting Complete ==')

# Test complete - logs data into database

# stock_id = 9395
# strategy = "crossover"
# start_date = '2020-04-20'
# end_date = '2020-06-20'
# set_cash = 100000
# run_id = 4

# conn = sqlite3.connect(config.DB_FILE)
# cursor = conn.cursor()

# backtest(stock_id, strategy, conn, start_date=start_date, end_date=end_date, \
#          run_id=run_id, set_cash=set_cash)
