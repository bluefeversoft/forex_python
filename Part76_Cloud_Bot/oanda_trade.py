from dateutil.parser import parse

class OandaTrade():
    def __init__(self, oanda_ob):
        self.unrealizedPL = float(oanda_ob['unrealizedPL'])
        self.currentUnits = int(oanda_ob['currentUnits'])
        self.trade_id = int(oanda_ob['id'])
        self.openTime = parse(oanda_ob['openTime'])
        self.instrument = oanda_ob['instrument']

    def __repr__(self):
        return str(vars(self))

    @classmethod
    def TradeFromAPI(cls, api_object):
        return OandaTrade(api_object)

    