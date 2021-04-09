import requests
import pandas as pd
from dateutil.parser import *
import defs
import utils
import sys
import json

class OandaAPI():

    def __init__(self):
        self.session = requests.Session()    

    def make_request(self, url, params={}, added_headers=None, verb='get', data=None, code_ok=200):

        headers = defs.SECURE_HEADER

        if added_headers is not None:   
            for k in added_headers.keys():
                headers[k] = added_headers[k]
                
        try:
            response = None
            if verb == 'post':
                response = self.session.post(url,params=params,headers=headers,data=data)
            elif verb == 'put':
                response = self.session.put(url,params=params,headers=headers,data=data)
            else:
                response = self.session.get(url,params=params,headers=headers,data=data)

            status_code = response.status_code

            if status_code == code_ok:
                json_response = response.json()
                return status_code, json_response
            else:
                return status_code, None   

        except:
            print("ERROR")
            return 400, None   

    def fetch_instruments(self):
        url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/instruments"
        status_code, data = self.make_request(url)
        return status_code, data
    
    def get_instruments_df(self):
        status_code, data = self.fetch_instruments()
        if status_code == 200:
            df = pd.DataFrame.from_dict(data['instruments'])
            return df[['name', 'type', 'displayName', 'pipLocation', 'marginRate']]
        else:
            return None
    
    def fetch_candles(self, pair_name, granularity="H1"):
        url = f"{defs.OANDA_URL}/instruments/{pair_name}/candles"

        params = dict(
            granularity = granularity,
            price = "MBA"
        )
        
        params['count'] = 10
        
        status_code, data = self.make_request(url, params=params)

        if status_code != 200:
            return status_code, None

        return status_code, OandaAPI.candles_to_df(data['candles'])

    def place_trade(self, pair, units):
        url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/orders"

        data = {
            "order": {
                "units": units,
                "instrument": pair,
                "timeInForce": "FOK",
                "type": "MARKET",
                "positionFill": "DEFAULT"
            }
        }

        status_code, json_data = self.make_request(url, verb='post', data=json.dumps(data), code_ok=201)

        if "orderFillTransaction" in json_data and "tradeOpened" in json_data["orderFillTransaction"]:
            return int(json_data["orderFillTransaction"]["tradeOpened"]["tradeID"])

        return None

        
    @classmethod
    def candles_to_df(cls, json_data):
        prices = ['mid', 'bid', 'ask']
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


if __name__ == "__main__":
    api = OandaAPI()
    res, df = api.fetch_candles("EUR_USD")
    print(df)
    