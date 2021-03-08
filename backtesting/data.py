# -*- coding: utf-8; py-indent-offset:4 -*-
import sys
sys.path.append("./")

import config
import numpy as np
import pandas as pd
import sqlite3

conn = sqlite3.connect(config.DB_FILE)

def create_dataframes(conn=conn):

    curve_df = pd.read_sql_query('SELECT * FROM curve_data', con=conn)
    curve_df['dotted'] = 100

    buynhold_df = pd.read_sql_query('SELECT * FROM buynhold_data', con=conn)

    return_df = pd.read_sql_query('SELECT * FROM return_data', con=conn)
    return_df["color"] = np.where(return_df["value"]<0, 'crimson', 'rgb(96,236,39,1)')

    return curve_df, buynhold_df, return_df