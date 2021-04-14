class TradeManager():

    def __init__(self, api, settings, log=None):
        self.api = api
        self.log = log
        self.settings = settings

    def log_message(self, msg):
        if self.log is not None:
            self.log.logger.debug(msg)
            
    def close_trades(self, pairs_to_close):

        open_trades, ok = self.api.open_trades()
        
        if ok == False:
            self.log_message("Error fetching open trades!!!!")
            return
        
        ids_to_close = [x.trade_id for x in open_trades if x.instrument in pairs_to_close]

        self.log_message(f"TradeManager:close_trades() pairs_to_close:{pairs_to_close} ")
        self.log_message(f"TradeManager:close_trades() open_trades:{open_trades} ")
        self.log_message(f"TradeManager:close_trades() ids_to_close:{ids_to_close} ")
        
        for t in ids_to_close:
            ok = self.api.close_trade(t)
            if ok == False:
                self.log_message(f"TradeManager:close_trades() {t} FAILED TO CLOSE ")
            else:
                self.log_message(f"TradeManager:close_trades() Closed")

    def create_trades(self, trades_to_make):
        for t in trades_to_make:
            trade_id = self.api.place_trade(t['pair'], t['units'])
            if trade_id is not None:
                self.log_message(f"TradeManager:Opened {trade_id} {t}")
            else:
                self.log_message(f"TradeManager:FAILED TO OPEN {t}")
            
    def place_trades(self, trades_to_make):
        self.log_message(f"TradeManager:place_trades() {trades_to_make}")
        pairs = [x['pair'] for x in trades_to_make]
        self.close_trades(pairs)
        self.create_trades(trades_to_make)