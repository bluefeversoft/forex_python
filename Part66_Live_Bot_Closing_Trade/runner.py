from oanda_api import OandaAPI

api = OandaAPI()

while True:
    command = input("Enter command:")
    if command == "T":
        print("Make a trade")
        trade_id, ok = api.place_trade("EUR_USD", 1000)
        print('trade_id', trade_id)
    if command == "C":
        print('Closing', trade_id)
        print(api.close_trade(trade_id))
    if command == "Q":
        break