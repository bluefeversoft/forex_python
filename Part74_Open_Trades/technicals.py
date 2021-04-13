import pandas as pd

from defs import BUY, SELL, NONE

class Technicals():
    
    def __init__(self, settings, api, pair, granularity, log=None):
        self.settings = settings
        self.log = log
        self.api = api
        self.pair = pair
        self.granularity = granularity
    
    def log_message(self, msg):
        if self.log is not None:
            self.log.logger.debug(msg)

    
    def fetch_candles(self, row_count, candle_time):
        status_code, df = self.api.fetch_candles(self.pair, count=row_count, granularity=self.granularity)
        if df is None:
            self.log_message(f"Error fetching candles for pair:{self.pair} {candle_time}, df None")
            return None
        elif df.iloc[-1].time != candle_time:
            self.log_message(f"Error fetching candles for pair:{self.pair} {candle_time} vs {df.iloc[-1].time}")
            return None
        else:
            return df

    
    def process_candles(self, df):

        df.reset_index(drop=True, inplace=True)
        df['PAIR'] = self.pair
        df['SPREAD'] = df.ask_c - df.bid_c
        
        short_prev = 'PREV_SHORT'
        long_prev = 'PREV_LONG'

        short_col = f'MA_{self.settings.short_ma}'
        long_col = f'MA_{self.settings.long_ma}'
        
        df[short_col] = df.mid_c.rolling(window=self.settings.short_ma).mean()
        df[long_col] = df.mid_c.rolling(window=self.settings.long_ma).mean()
        
        df[short_prev] = df[short_col].shift(1)
        df[long_prev] = df[long_col].shift(1)
        
        df['D_PREV'] = df[short_prev] - df[long_prev]
        df['D_NOW'] = df[short_col] - df[long_col]
        
        last = df.iloc[-1]
        decision = NONE

        if last.D_NOW < 0 and last.D_PREV > 0:
            decision = SELL
        elif last.D_NOW > 0 and last.D_PREV < 0:
            decision = BUY

        log_cols = ['time','volume','mid_c','SPREAD','PAIR',short_col,long_col,short_prev,long_prev ,'D_PREV','D_NOW']
        self.log_message(f"Processed_df\n{df[log_cols].tail(2)}")
        self.log_message(f"Trade_decision:{decision}")
        self.log_message("")

        return decision


    def get_trade_decision(self, candle_time):

        max_rows = self.settings.long_ma + 2
        self.log_message("")
        self.log_message(f"get_trade_decision() pair:{self.pair} max_rows:{max_rows}")

        df = self.fetch_candles(max_rows, candle_time)

        if df is not None:
            return self.process_candles(df)

        return NONE

        






















