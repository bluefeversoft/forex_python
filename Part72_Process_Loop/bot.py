import pprint
import time

from settings import Settings
from log_wrapper import LogWrapper
from timing import Timing
from oanda_api import OandaAPI

GRANULARITY = "M1"
SLEEP = 10.0

class TradingBot():
    
    def __init__(self):    
        self.log = LogWrapper("TradingBot")
        self.trade_pairs = Settings.get_pairs()
        self.settings = Settings.load_settings()
        self.api = OandaAPI()
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
        for pair in self.trade_pairs:
            if self.timings[pair].ready == True:
                self.log_message(f"Ready to trade {pair}") 

    
    def run(self):
        while True:
            print('update_timings()...')
            self.update_timings()
            print('process_pairs()...')
            self.process_pairs()
            print('sleep()...')
            time.sleep(SLEEP)


if __name__ == "__main__":
    b = TradingBot()
    b.run()