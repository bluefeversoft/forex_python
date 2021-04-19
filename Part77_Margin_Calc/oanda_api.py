import requests
import pandas as pd
from dateutil.parser import *
import defs
import utils
import sys
import json

from oanda_trade import OandaTrade
from oanda_price import OandaPrice

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

    def fetch_instruments(self, pair_list=None):

        url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/instruments"
        params = None
        if pair_list is not None:
            params = dict(
                instruments = ','.join(pair_list)
            )

        status_code, data = self.make_request(url, params=params)
        return status_code, data
    
    def get_instruments_df(self):
        status_code, data = self.fetch_instruments()
        if status_code == 200:
            df = pd.DataFrame.from_dict(data['instruments'])
            return df[['name', 'type', 'displayName', 'pipLocation', 'marginRate']]
        else:
            return None
    
    def fetch_candles(self, pair_name, count=10, granularity="H1"):
        url = f"{defs.OANDA_URL}/instruments/{pair_name}/candles"

        params = dict(
            granularity = granularity,
            price = "MBA"
        )
        
        params['count'] = count
        
        status_code, data = self.make_request(url, params=params)

        if status_code != 200:
            return status_code, None

        return status_code, OandaAPI.candles_to_df(data['candles'])

    def last_complete_candle(self, pair_name, granularity="H1"):
        code, df = self.fetch_candles(pair_name, granularity=granularity)
        if df is None or df.shape[0] == 0:
            return None
        return df.iloc[-1].time    
    
    def close_trade(self, trade_id):
        url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/trades/{trade_id}/close"
        status_code, json_data = self.make_request(url, verb='put', code_ok=200)
        if status_code != 200:
            return False
        return True

    def set_sl_tp(self, price, order_type, trade_id):
        url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/orders"
        data = {
            "order": {
                "timeInForce": "GTC",
                "price": str(price), 
                "type": order_type,
                "tradeID": str(trade_id)
            }
        }
        status_code, json_data = self.make_request(url, verb='post', data=json.dumps(data), code_ok=201)

        if status_code != 201:
            return False
        return True

    def place_trade(self, pair, units, take_profit=None, stop_loss=None):
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

        if status_code != 201:
            return None

        trade_id = None
        ok = True

        if "orderFillTransaction" in json_data and "tradeOpened" in json_data["orderFillTransaction"]:
            trade_id = int(json_data["orderFillTransaction"]["tradeOpened"]["tradeID"])
            if take_profit is not None:
                if(self.set_sl_tp(take_profit, "TAKE_PROFIT", trade_id) == False):
                    ok = False
            if stop_loss is not None:
                if(self.set_sl_tp(stop_loss, "STOP_LOSS", trade_id) == False):
                    ok = False

        return trade_id, ok

    
    def open_trades(self):
        url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/openTrades"
        status_code, data = self.make_request(url)
        
        if status_code != 200:
            return [], False

        if 'trades' not in data:
            return [], True

        trades = [OandaTrade.TradeFromAPI(x) for x in data['trades']]       

        return trades, True

    def fetch_prices(self, pair_list):
        url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/pricing"
        
        params = dict(
            instruments = ','.join(pair_list)
        )       
        
        status_code, data = self.make_request(url, params=params)

        if status_code != 200:
            return status_code, None

        prices = { x['instrument']: OandaPrice.PriceFromAPI(x) for x in data['prices'] }
        return status_code, prices
        
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
    
    code, prices = api.fetch_prices(['EUR_USD', 'SGD_CHF'])
    print(prices)

    