import pprint
import time

from settings import Settings
from log_wrapper import LogWrapper
from timing import Timing
from oanda_api import OandaAPI
from technicals import Technicals
from defs import NONE, BUY, SELL
from trade_manager import TradeManager

GRANULARITY = "M1"
SLEEP = 10.0

class TradingBot():
    
    def __init__(self):    
        self.log = LogWrapper("Bot")
        self.tech_log = LogWrapper("Technicals")
        self.trade_log = LogWrapper("Trade")
        self.trade_pairs = Settings.get_pairs()
        self.settings = Settings.load_settings()
        self.api = OandaAPI()
        self.trade_manager = TradeManager(self.api, self.settings, self.trade_log)
        self.timings = { p: Timing(self.api.last_complete_candle(p, GRANULARITY)) for p in self.trade_pairs }
        self.log_message(f"Bot started with\n{pprint.pformat(self.settings)}")
        self.log_message(f"Bot Timings\n{pprint.pformat(self.timings)}")
        
    def log_message(self, msg):
        self.log.logger.debug(msg)       
    
    def update_timings(self):        
        for pair in self.trade_pairs:
            current = self.api.last_complete_candle(pair, GRANULARITY)
            self.timings[pair].ready = False
            if current > self.timings[pair].last_candle:
                self.timings[pair].ready = True
                self.timings[pair].last_candle = current
                self.log_message(f"{pair} new candle {current}")

    def process_pairs(self):      
        trades_to_make = []
        for pair in self.trade_pairs:
            if self.timings[pair].ready == True:
                self.log_message(f"Ready to trade {pair}") 
                techs = Technicals(self.settings[pair], self.api, pair, GRANULARITY, log=self.tech_log)
                decision = techs.get_trade_decision(self.timings[pair].last_candle)
                units = decision * self.settings[pair].units
                if units != 0:
                    trades_to_make.append({'pair': pair, 'units': units})

        if len(trades_to_make) > 0:
            print(trades_to_make)
            self.trade_manager.place_trades(trades_to_make)
        
    
    def run(self):
        while True:
            self.update_timings()
            self.process_pairs()
            time.sleep(SLEEP)


if __name__ == "__main__":
    b = TradingBot()
    b.run()