from oanda_api import OandaAPI

class TradeUnitCalculator():
    def __init__(self, api, pairs_list):
        self.api = api
        self.pairs_list = pairs_list
        ok, instruments_raw = api.fetch_instruments(pairs_list)
        self.marginRates = { x['name'] : float(x['marginRate']) for x in instruments_raw['instruments'] }
        ok, self.prices = api.fetch_prices(pairs_list)


    def get_trade_margin_for_units(self, units, pair):
        marginRate = self.marginRates[pair]
        price = self.prices[pair]

        trade_margin = price.mid * marginRate * price.mid_conv * units
        return trade_margin
        

    def get_units_for_margin(self, margin, pair):
        marginRate = self.marginRates[pair]
        price = self.prices[pair]

        units = margin / (price.mid * marginRate * price.mid_conv)
        return int(units)

if __name__ == "__main__":
    api = OandaAPI()
    pairs = ['EUR_USD', 'GBP_JPY', 'AUD_NZD', 'SGD_CHF']
    r = TradeUnitCalculator(api, pairs)
    for p in pairs:
        print( 
            p, 
            round(r.get_trade_margin_for_units(10000, p),2),            
            r.get_units_for_margin(2000, p)
            )