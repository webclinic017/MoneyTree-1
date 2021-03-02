# -*- coding: utf-8; py-indent-offset:4 -*-
import os, sqlite3, config, sys
import pandas as pd
import backtrader as bt
from report import Cerebro
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

selected_strat = "opening_range_breakout"

sid = 9395

conn = sqlite3.connect(config.DB_FILE)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print(f"== Testing {sid} ==")

df = pd.read_sql("""
        SELECT datetime, open, high, low, close, volume
        FROM stock_price_minute
        WHERE stock_id = :stock_id
        AND strftime('%H:%M:%S', datetime) >= '09:30:00'
        AND strftime('%H:%M:%S', datetime) <= '16:00:00'
        ORDER BY datetime ASC
        LIMIT 20000
""", conn, params={"stock_id": sid}, index_col='datetime', parse_dates=['datetime'])

# initialize Cerebro engine, extende with report method
cerebro = Cerebro()
cerebro.broker.setcash(25000)
cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

# add data
feed = bt.feeds.PandasData(dataname=df)
cerebro.adddata(feed)

if selected_strat == 'opening_range_breakout':
    cerebro.addstrategy(strategy=OpeningRangeBreakout)
else:
    # add Golden Cross strategy
    params = (('fast', 50),
            ('slow', 200),
            )
    # cerebro.addstrategy(strategy=CrossOver, **dict(params))
    cerebro.addstrategy(strategy=CrossOver, **dict(params))

# run backtest with both plotting and reporting
cerebro.run()

saveplots(cerebro, file_path = 'savefig.png') #run it

cerebro.report(conn, outputdir='/Users/kylespringfield/Dev/MoneyTree/backtest_reports', memo='run_id')
