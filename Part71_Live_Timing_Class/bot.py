import pprint

from settings import Settings
from log_wrapper import LogWrapper
from timing import Timing
from oanda_api import OandaAPI

GRANULARITY = "M1"

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


if __name__ == "__main__":
    b = TradingBot()