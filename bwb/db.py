# -*- coding: utf-8 -*-
import pandas as pd
import pandas_datareader.data as web
import datetime, os
from datetime import datetime as dt
from datetime import timedelta as td
import yfinance as yf

try:
    from . import customstrategy as cst
except:
    import customstrategy as cst



class LocalDB():
    curdir = os.getcwd() + "/LocalDB/"
    db_ext = 'csv'

    def __init__(self, db_dir = curdir, db_ext = db_ext):
        if not os.path.exists(db_dir): os.mkdir(db_dir)
        self.db_dir, self.db_ext = db_dir, db_ext

    def loader(self, issue, start, end = datetime.date.today(), source = 'yahoo'):
        self.db_dir_issue = self.db_dir + issue + '/'
        if not os.path.exists(self.db_dir_issue): os.mkdir(self.db_dir_issue)
        update = False
        if (type(start) is str):
            start = dt.strptime(start, '%Y/%m/%d')
        if (type(end) is str):
            end = dt.strptime(end, '%Y/%m/%d')
        file_path = self.db_dir_issue + 'candle.' + self.db_ext
        start_dt = start.date() + td(days=1)
        start_str = start_dt.strftime('%Y/%m/%d')
        try:
            end_dt = end.date() - td(days=1)
        except:
            end_dt = end - td(days=1)
        end_str = end_dt.strftime('%Y/%m/%d')
        if not os.path.exists(file_path):
            df = self._reader(issue, start_str, end_str, source)
            update = True
        else:
            if self.db_ext == 'csv':
                df = pd.read_csv(file_path, index_col=0)
            df.insert(0, 'Date', df.index.values)
            start_db_dt = dt.strptime(df['Date'].values[0], '%Y-%m-%d') - td(days=1)
            start_db_str = start_db_dt.strftime('%Y/%m/%d')
            end_db_dt = dt.strptime(df['Date'].values[-1], '%Y-%m-%d') + td(days=1)
            end_db_str = end_db_dt.date().strftime('%Y/%m/%d')
            if start_dt < start_db_dt.date():
                df_start = self._reader(issue, start_str, start_db_str, source)
                df_start['Date'] = df_start['Date'].astype(str)
                df_start['Volume'] = df_start['Volume'].astype(float)
                df = pd.concat([df_start, df], axis=0)
                update = True
            if (end_dt >= end_db_dt.date()) and  (type(end_dt) is not datetime.datetime):
                df_end = self._reader(issue, end_str, end_db_str, source)
                df_end['Date'] = df_end['Date'].astype(str)
                df_end['Volume'] = df_end['Volume'].astype(float)
                df = pd.concat([df, df_end[1:]], axis=0)
                update = True
        df = df[~df.duplicated(subset='Date')]
        df.index = pd.to_datetime(df.index)
        if (self.db_ext == 'csv') and update:
            df.to_csv(file_path, index = None)
        return df


    @staticmethod
    def _reader(issue, start, end, source):
        yf.pdr_override()
        start = dt.strptime(start, '%Y/%m/%d')
        end = dt.strptime(end, '%Y/%m/%d')
        df = web.get_data_yahoo(issue, data_source='yahoo', start=start, end=end)
        df.insert(0, 'Date', df.index)
        return df

    def saver(self, df, issue, name):
        df.to_csv(self.db_dir + issue + '/' + str(name) + '.csv')
    
    def runsaver(self, strategy, candle, issue):
        strategy.candle = candle
        strategy_name = str(strategy.__name__)
        strategy_dir =self.db_dir + issue + '/' + strategy_name + '/'
        if not os.path.exists(strategy_dir): os.mkdir(strategy_dir)
        tester = cst.Btest(
            strategy = strategy,
            cash = 1000,
            commission = 0.00495,
            margin = 1.0,
            trade_on_close = True,
            exclusive_orders = True
            )
        # tester = cst.Btest(strategy)
        output = tester.run()

        equity = output['_equity_curve']
        trade = output['_trades']
        self.saver(equity, issue,  strategy_name + '/equity')
        self.saver(trade, issue, strategy_name + '/trade')
        self.saver(output, issue, strategy_name + '/all')
        return output

if __name__ == '__main__':
    d = LocalDB()
    myd = d.loader('AAPL', '2018/11/01', end = '2021/06/01')