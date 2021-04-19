class OandaPrice():
    def __init__(self, pair, ask, bid, sell_conv, buy_conv):
        self.pair = pair
        self.ask = ask
        self.bid = bid
        self.mid = (ask - bid) + bid
        self.sell_conv = sell_conv
        self.buy_conv = buy_conv
        self.mid_conv = (buy_conv + sell_conv) / 2
    
    def __repr__(self):
        return str(vars(self))

    @classmethod
    def PriceFromAPI(cls, price_object):
        return OandaPrice(
            pair = price_object['instrument'],
            ask = float(price_object['asks'][0]['price']),
            bid = float(price_object['bids'][0]['price']),
            sell_conv = float(price_object['quoteHomeConversionFactors']['negativeUnits']),
            buy_conv = float(price_object['quoteHomeConversionFactors']['positiveUnits'])
        )
    