import pprint

from settings import Settings
from log_wrapper import LogWrapper

class TradingBot():
    
    def __init__(self):    
        self.log = LogWrapper("TradingBot")
        self.trade_pairs = Settings.get_pairs()
        self.settings = Settings.load_settings()
        self.log_message(f"Bot started with\n{pprint.pformat(self.settings)}")
        
    def log_message(self, msg):
        self.log.logger.debug(msg)


if __name__ == "__main__":
    b = TradingBot()