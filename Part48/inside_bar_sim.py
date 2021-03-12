import pandas as pd
import datetime as dt
import utils
import instrument

SLOSS = 0.4
TPROFIT = 0.8

ENTRY_PRC = 0.1
BUY = 1
SELL = -1
NONE = 0

LOSS_FRACTION = -1.0
GAIN_FRACTION = TPROFIT / SLOSS

def direction(row):
    if row.mid_c > row.mid_o:
        return BUY
    return SELL

def get_signal(row):
    if row.mid_h_prev > row.mid_h and row.mid_l_prev < row.mid_l:
        return row.DIRECTION_prev
    return 0

def get_entry_stop(row):
    if row.SIGNAL == BUY:
        return (row.RANGE_prev * ENTRY_PRC) + row.ask_h_prev
    elif row.SIGNAL == SELL:
        return row.bid_l_prev - (row.RANGE_prev * ENTRY_PRC)
    else:
        return NONE

def get_stop_loss(row):
    if row.SIGNAL == BUY:
        return row.ENTRY - (row.RANGE_prev * SLOSS)
    elif row.SIGNAL == SELL:
        return row.ENTRY + (row.RANGE_prev * SLOSS)
    else:
        return NONE


def get_take_profit(row):
    if row.SIGNAL == BUY:
        return row.ENTRY + (row.RANGE_prev * TPROFIT)
    elif row.SIGNAL == SELL:
        return row.ENTRY - (row.RANGE_prev * TPROFIT)
    else:
        return NONE

def triggered(direction, current_price, signal_price):
    if direction == BUY and current_price > signal_price:
        return True
    elif direction == SELL and current_price < signal_price:
        return True
    return False

def end_hit_calc(direction, SL, price, start_price):
    delta = price - start_price
    full_delta = start_price - SL
    fraction = abs(delta / full_delta)
   
    if direction == BUY and price >= start_price:
        return fraction
    elif direction == BUY and price < start_price:
        return -fraction
    elif direction == SELL and price <= start_price:
        return fraction
    elif direction == SELL and price > start_price:
        return -fraction


def process_buy(TP, SL, ask_prices, bid_prices, entry_price):
    for index, price in enumerate(ask_prices):
        if triggered(BUY, price, entry_price) == True:
            for live_price in bid_prices[index:]:
                if live_price >= TP:
                    return GAIN_FRACTION
                elif live_price <= SL:
                    return LOSS_FRACTION
            return end_hit_calc(BUY, SL, live_price, entry_price)
    return 0.0

def process_sell(TP, SL, ask_prices, bid_prices, entry_price):
    for index, price in enumerate(bid_prices):
        if triggered(SELL, price, entry_price) == True:
            for live_price in ask_prices[index:]:
                if live_price <= TP:
                    return GAIN_FRACTION
                elif live_price >= SL:
                    return LOSS_FRACTION
            return end_hit_calc(SELL, SL, live_price, entry_price)
    return 0.0

def get_test_pairs(pair_str):
    existing_pairs = instrument.Instrument.get_instruments_dict().keys()
    pairs = pair_str.split(",")
    
    test_list = []
    for p1 in pairs:
        for p2 in pairs:
            p = f"{p1}_{p2}"
            if p in existing_pairs:
                test_list.append(p)
    
    return test_list

def get_trades_df(df_raw):
    df = df_raw.copy()

    df['RANGE'] = df.mid_h - df.mid_l
    df['mid_h_prev'] = df.mid_h.shift(1)
    df['mid_l_prev'] = df.mid_l.shift(1)
    df['ask_h_prev'] = df.ask_h.shift(1)
    df['bid_l_prev'] = df.bid_l.shift(1)
    df['RANGE_prev'] = df.RANGE.shift(1)
    df['DIRECTION'] = df.apply(direction, axis=1)
    df['DIRECTION_prev'] = df.DIRECTION.shift(1).fillna(0).astype(int)

    df.dropna(inplace=True)
    
    df['SIGNAL'] = df.apply(get_signal, axis=1)
    df['ENTRY'] = df.apply(get_entry_stop, axis=1)
    df['STOPLOSS'] = df.apply(get_stop_loss, axis=1)
    df['TAKEPROFIT'] = df.apply(get_take_profit, axis=1)

    df_trades = df[df.SIGNAL!=NONE].copy()
    df_trades["next"] = df_trades["time"].shift(-1)
    df_trades['trade_end'] = df_trades.next + dt.timedelta(hours=3, minutes=55)
    df_trades['trade_start'] = df_trades.time + dt.timedelta(hours=4)
    
    df.dropna(inplace=True)
    df_trades.reset_index(drop=True, inplace=True)

    return df_trades

def evaluate_pair(df_trades, m5_data):
    total = 0
    for index, row in df_trades.iterrows():
        m5_slice = m5_data[(m5_data.time >= row.trade_start) & (m5_data.time <= row.trade_end)]
        if row.SIGNAL == BUY:
            r = process_buy(row.TAKEPROFIT, row.STOPLOSS, m5_slice.ask_c.values, m5_slice.bid_c.values, row.ENTRY)
            total += r
        else:
            r = process_sell(row.TAKEPROFIT, row.STOPLOSS, m5_slice.ask_c.values, m5_slice.bid_c.values, row.ENTRY)
            total += r
    return total

def run():
    currencies = "GBP,EUR,USD,CAD,JPY,NZD,CHF"
    test_pairs = get_test_pairs(currencies)    

    grand_total = 0
    for pairname in test_pairs:

        i_pair = instrument.Instrument.get_instruments_dict()[pairname]

        h4_data = pd.read_pickle(utils.get_his_data_filename(pairname, "H4"))
        m5_data = pd.read_pickle(utils.get_his_data_filename(pairname, "M5"))

        df_trades = get_trades_df(h4_data)

        score = evaluate_pair(df_trades, m5_data)
        grand_total += score
        print(f"{pairname} {score:.0f}")
    print(f"TOTAL {grand_total:.0f}")


if __name__ == "__main__":
    run()