import pandas as pd
import utils
import instrument
pd.set_option('display.max_columns', None)

def is_trade(row):
    if row.DIFF >= 0 and row.DIFF_PREV < 0:
        return 1
    if row.DIFF <= 0 and row.DIFF_PREV > 0:
        return -1
    return 0 


def get_ma_col(ma):
    return f"MA_{ma}"


def evaluate_pair(i_pair, mashort, malong, price_data):

    price_data['DIFF'] = price_data[get_ma_col(mashort)] - price_data[get_ma_col(malong)]
    price_data['DIFF_PREV'] = price_data.DIFF.shift(1)
    price_data['IS_TRADE'] = price_data.apply(is_trade, axis=1)
    
    df_trades = price_data[price_data.IS_TRADE!=0].copy()
    df_trades["DELTA"] = (df_trades.mid_c.diff() / i_pair.pipLocation).shift(-1)
    df_trades["GAIN"] = df_trades["DELTA"] * df_trades["IS_TRADE"]

    print(f"{i_pair.name} {mashort} {malong} trades:{df_trades.shape[0]} gain:{df_trades['GAIN'].sum():.0f}")

    return df_trades['GAIN'].sum()


def get_price_data(pairname, granularity):
    df = pd.read_pickle(utils.get_his_data_filename(pairname, granularity))
    
    non_cols = ['time', 'volume']
    mod_cols = [x for x in df.columns if x not in non_cols]
    df[mod_cols] = df[mod_cols].apply(pd.to_numeric)

    return df[['time', 'mid_c']]


def process_data(ma_short, ma_long, price_data):
    ma_list = set(ma_short + ma_long)
    
    for ma in ma_list:  
        price_data[get_ma_col(ma)] = price_data.mid_c.rolling(window=ma).mean()
    
    return price_data


def run():
    pairname = "EUR_CHF"
    granularity = "H1"
    ma_short = [8, 16, 32, 64]
    ma_long = [32, 64, 96, 128, 256]
    i_pair = instrument.Instrument.get_instruments_dict()[pairname]

    price_data = get_price_data(pairname, granularity)
    price_data = process_data(ma_short, ma_long, price_data)

    best = -1000000.0
    b_mashort = 0
    b_malong = 0
    
    for _malong in ma_long:
        for _mashort in ma_short:
            if _mashort >= _malong:
                continue
            res = evaluate_pair(i_pair, _mashort, _malong, price_data.copy())
            if res > best:
                best = res
                b_mashort = _mashort
                b_malong = _malong

    print(f"Best:{best:.0f} MASHORT:{b_mashort:.0f} MALONG:{b_malong:.0f}")


if __name__ == "__main__":
    run()