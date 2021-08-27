# -*- coding: utf-8 -*-
import pandas as pd
import pandas_datareader.data as web
import datetime, os
from datetime import datetime as dt
from datetime import timedelta as td
import yfinance as yf
from abc import ABCMeta, abstractmethod

from pycheck.variable import info

try:
    from . import basicstrategy as bst
except:
    import basicstrategy as bst

GET_CANDDLE = 'yfinance'

def str_to_date(t):
    return dt.strptime(t, '%Y-%m-%d').date()

def datetime_to_date(t):
    return t.date()

def get_today():
    return datetime.date.today()

class ObjectDB(metaclass = ABCMeta):
    @abstractmethod
    def reader(self):
        pass

    @abstractmethod
    def loader(self):
        pass

    @abstractmethod
    def saver(self):
        pass

    @staticmethod
    def is_str(v):
        return type(v) is str
    
    @staticmethod
    def is_path(path):
        return os.path.exists(path)
    
    def is_renew(self):
        return (self.start < self.df_candle.index[0]) or (self.end > self.df_candle.index[-1]+td(days=1))
    
    def add_path(self, path):
        if (not self.is_path(path)) and ('.' not in path): os.mkdir(path)

    def get_candle_from_yfinance(self):
        '''
        standard output
            $start:(input 0714, output 0713), $end :(input 0721, output 0720)
        $start is to +1, $end is to stay the same.
        In Japan, the US market starts at night and ends in the morning.
        Therefore, it is better to get the stock price one day before Japan time (=end) while the US market is closed.
        '''
        yf.pdr_override()
        return web.get_data_yahoo(self.issue, data_source='yahoo', start=self.start+td(days=1), end=self.end)
        
    def get_df_candle(self):
        if GET_CANDDLE == 'yfinance':return self.get_candle_from_yfinance()

    def set_period(self, start, end):
        self.start, self.end = str_to_date(start), str_to_date(end)
    
class LocalDB(ObjectDB):
    def basic_format():
        return 'csv'

    def get_path_localdb():
        return os.getcwd() + "/LocalDB/"

    @staticmethod
    def init_path(root):
        return {
                'LocalDB':root,
                }

    def __init__(self, path_localdb=get_path_localdb(), save_format=basic_format()):
        self.save_format = save_format
        self.init_db(path_localdb)

    def init_db(self, root):
        self.path = self.init_path(root)
        self.reflect_path()
    
    def reflect_path(self):
        for path in self.path.values():
            self.add_path(path)

    def reader(self):
        if self.save_format=='csv':
            self.df_candle = pd.read_csv(self.path['candle'], index_col=0)
            self.df_candle.index = pd.to_datetime(self.df_candle.index, dayfirst=True)
    
    def loader(self, issue, start, end):
        print(issue)
        self.set_period(start, end)
        self.issue = issue
        self.path['issue'] = self.path['LocalDB'] + issue + '/'
        self.path['candle']= self.path['issue'] + 'candle.' + self.save_format
        self.reflect_path()
        # xxx/candle.csv is not found
        if not self.is_path(self.path['candle']):
            self.df_candle = self.get_df_candle()
            self.saver(self.df_candle, self.path['candle'])
        # xxx/candle.csv is found
        else:
            self.reader()
            # renew candle
            if self.is_renew():self.saver(self.df_candle, self.path['candle'])
        return self.df_candle
    
    def saver(self, df, path):
        df.to_csv(path)
    
    def runsaver(self, strategy):
        self.path['strategy'] = self.path['issue'] + str(self.start) + '_' + str(self.end) + '_' + str(strategy.__name__) + '/'
        self.path['equity'] = self.path['strategy'] + 'equity.' + self.save_format
        self.path['trade'] = self.path['strategy'] + 'trade.' + self.save_format
        self.path['result'] = self.path['strategy'] + 'overview.' + self.save_format
        self.reflect_path()
        tester = bst.Btest(
            strategy = strategy,
            cash = 1000,
            commission = 0.00495,
            margin = 1.0,
            trade_on_close = True,
            exclusive_orders = True
            )
        df_result = tester.run()
        tester.htmlsaver(self.path['strategy'] + 'bokeh')
        df_equity = df_result['_equity_curve']
        df_trade = df_result['_trades'].set_index('Size')
        self.saver(df_equity, self.path['equity'])
        self.saver(df_trade, self.path['trade'])
        self.saver(df_result, self.path['result'])
        return df_result