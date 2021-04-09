import pandas as pd
import datetime as dt
from oanda_api import OandaAPI
import json

PAIRS = ['GBP_USD', 'GBP_CAD', 'GBP_JPY', 'GBP_NZD', 
'GBP_CHF', 'EUR_GBP', 'EUR_USD', 'EUR_CAD', 'EUR_JPY', 
'EUR_NZD', 'EUR_CHF', 'USD_CAD', 'USD_JPY', 'USD_CHF', 
'CAD_JPY', 'CAD_CHF', 'NZD_USD', 'NZD_CAD', 'NZD_JPY', 
'NZD_CHF', 'CHF_JPY']

DF_COLS = ['PAIR', 'time', 'volume', 'mid_o', 'mid_h', 'mid_l', 'mid_c', 'MACD_CROSS', 'BB_SIGNAL',
            'BODY_PERC', 'DIRECTION', 'HAMMER', 'DOJI', 'MARUBOZU',
       'SPINNING_TOP', 'ENGULFING', 'TREND']

SMALL_BODY = 0.20
CLOSE_DISTANCE = 0.15
DOJI_BODY = 0.05
FULL_BODY = 0.95
CENTER_DISTANCE_HIGH = 0.55
CENTER_DISTANCE_LOW = 0.45
BIG_BODY = 0.6
ENGULFING_FACTOR = 1.1

def apply_top_end_distance(row):
    if row.DIRECTION == 1:
        return row.mid_h - row.mid_c
    else:
        return row.mid_h - row.mid_o

def apply_bottom_end_distance(row):
    if row.DIRECTION == 1:
        return row.mid_o - row.mid_l
    else:
        return row.mid_c - row.mid_l

def apply_hammer(row):
    if row.BODY_PERC < SMALL_BODY:
        if row.DIST_TOP_PERC < CLOSE_DISTANCE or row.DIST_BOTTOM_PERC < CLOSE_DISTANCE:
            return True
    return False

def apply_spinning_top(row):
    if row.BODY_PERC < SMALL_BODY:
        if row.DIST_TOP_PERC < CENTER_DISTANCE_HIGH and row.DIST_TOP_PERC > CENTER_DISTANCE_LOW:
            return True
    return False

def engulfing(row):
    if row.PREV_DIRECTION != row.DIRECTION:
        if row.PREV_BODY_PERC > BIG_BODY and row.BODY_PERC > BIG_BODY:
            if row.BODY_RANGE > row.PREV_BODY_RANGE * ENGULFING_FACTOR:
                return True
    return False

def apply_stats(df):
    df['RANGE'] = df.mid_h - df.mid_l
    df['BODY_RANGE'] = abs(df.mid_c - df.mid_o)
    df['CENTER'] = (df.mid_h - df.mid_l) / 2 + df.mid_l
    df['BODY_PERC'] = df.BODY_RANGE / df.RANGE
    df['DIRECTION'] = df.mid_c - df.mid_o
    df['DIRECTION'] = df['DIRECTION'].apply(lambda x: 1 if x >= 0 else -1)

    df['DIST_TOP'] = df.apply(apply_top_end_distance, axis=1)
    df['DIST_BOTTOM'] = df.apply(apply_bottom_end_distance, axis=1)

    df['DIST_TOP_PERC'] = df.DIST_TOP / df.RANGE
    df['DIST_BOTTOM_PERC'] = df.DIST_BOTTOM / df.RANGE

    df['PREV_BODY_RANGE'] = df.BODY_RANGE.shift(1)
    df['PREV_BODY_PERC'] = df.BODY_PERC.shift(1)
    df['PREV_DIRECTION'] = df.DIRECTION.shift(1)

    df.dropna(inplace=True)
    return df

def apply_patterns(df):
    df['HAMMER'] = df.apply(apply_hammer, axis=1)
    df['DOJI'] = df['BODY_PERC'].apply(lambda x: True if x < DOJI_BODY else False)
    df['MARUBOZU'] = df['BODY_PERC'].apply(lambda x: True if x > FULL_BODY else False)
    df['SPINNING_TOP'] = df.apply(apply_spinning_top, axis=1)
    df['ENGULFING'] = df.apply(engulfing, axis=1)
    return df

def is_cross(row, val_now, val_prev):    
    if row[val_now] >= 0 and row[val_prev] < 0:
        return 1
    if row[val_now] <= 0 and row[val_prev] > 0:
        return -1
    return 0  

def is_trend(row):    
    if row.EMA_SM > row.EMA_MD and row.EMA_MD > row.EMA_LN:
        return 1  
    if row.EMA_SM < row.EMA_MD and row.EMA_MD < row.EMA_LN:
        return -1
    return 0  

def Get_BB_Signal(row):
    if row.mid_c > row.BB_UPPER and row.mid_c > row.mid_o:
        return 1
    if row.mid_c < row.BB_LOWER and row.mid_c < row.mid_o:
        return 1
    return 0

def BBands(df):
    df['TP'] = (df.mid_h + df.mid_l + df.mid_c) / 3
    df['MA_TP'] = df.TP.rolling(window=20).mean()
    df['MA_STD'] = df.TP.rolling(window=20).std()
    df['BB_UPPER'] = df.MA_TP + 2 * df.MA_STD
    df['BB_LOWER'] = df.MA_TP - 2 * df.MA_STD
    df['BB_SIGNAL'] = df.apply(Get_BB_Signal, axis=1)
    return df

def Macd(df):
    df['EMA_LONG'] = df.mid_c.ewm(span=26, min_periods=26).mean()
    df['EMA_SHORT'] = df.mid_c.ewm(span=12, min_periods=12).mean()
    df['MACD'] = df.EMA_SHORT - df.EMA_LONG
    df['SIGNAL'] = df.MACD.ewm(span=9).mean()
    df['HIST'] = df.MACD - df.SIGNAL
    df['PREV_HIST'] = df.HIST.shift(1)
    df['MACD_CROSS'] = df.apply(is_cross, val_now='HIST', val_prev='PREV_HIST', axis=1)
    return df

def apply_trend(df):
    df[f'EMA_SM'] = df.mid_c.ewm(span=8, min_periods=8).mean()
    df[f'EMA_MD'] = df.mid_c.ewm(span=20, min_periods=20).mean()
    df[f'EMA_LN'] = df.mid_c.ewm(span=50, min_periods=50).mean()

    df['TREND'] = df.apply(is_trend, axis=1)
    return df
    

def get_pair_data(pair, api):
    code, df = api.fetch_candles(pair, granularity='M5')

    df['PAIR'] = pair
   
    if code == 200:
        df = Macd(df)
        df = BBands(df)
        df = apply_stats(df)
        df = apply_patterns(df)
        df = apply_trend(df)
        df.dropna(inplace=True)
        df = df[DF_COLS]
        return df.iloc[-1:]
    return None

def prepare_data():
    api = OandaAPI()
    data = []
    for p in PAIRS:
        row = get_pair_data(p, api)
        if row is not None:
            data.append(row)

    final_df = pd.concat(data)
    final_df['time'] = [dt.datetime.strftime(x, "%Y-%m-%d %H:%M:%S") for x in final_df.time]
    return json.dumps(final_df.to_dict(orient='records'))

if __name__ == "__main__":
    with open('static/data.json', 'w') as f:
        f.write(prepare_data())
    






