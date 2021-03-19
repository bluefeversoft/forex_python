import requests
import pandas as pd
from dateutil.parser import *
import defs

class OandaAPI():

    def __init__(self):
        self.session = requests.Session()    

    def fetch_instruments(self):
        url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/instruments"
        response = self.session.get(url, params=None, headers=defs.SECURE_HEADER)
        return response.status_code, response.json()
    
    def get_pairs_list(self):
        code, data = self.fetch_instruments()
        if code == 200:
            return [x for x in data['instruments']]
        else:
            return None    

    def fetch_candles(self, pair_name, count=100, granularity="H1"):
        url = f"{defs.OANDA_URL}/instruments/{pair_name}/candles"

        params = dict(
            granularity = granularity,
            price = "M"
        )        
        params['count'] = count

        print(url, params)

        response = self.session.get(url, params=params, headers=defs.SECURE_HEADER)

        if response.status_code != 200:
            return response.status_code, None

        json_data =  response.json()['candles']
        return response.status_code, OandaAPI.candles_to_df(json_data)

    @classmethod
    def candles_to_df(cls, json_data):
        prices = ['mid']
        ohlc = ['o', 'h', 'l', 'c']

        our_data = []
        for candle in json_data:
            if candle['complete'] == False:
                continue
            new_dict = {}
            new_dict['time'] = candle['time']
            new_dict['volume'] = candle['volume']
            for price in prices:
                for oh in ohlc:
                    new_dict[f"{price}_{oh}"] = float(candle[price][oh])
            our_data.append(new_dict)
        df = pd.DataFrame.from_dict(our_data)
        df["time"] = [parse(x) for x in df.time] 
        return df
