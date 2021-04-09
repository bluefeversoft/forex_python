import pandas as pd
from dateutil.parser import *

import utils
import instrument
import ma_result
from ma_excel import create_excel

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

    price_data = price_data[['time', 'mid_c', get_ma_col(mashort), get_ma_col(malong)]].copy()

    price_data['DIFF'] = price_data[get_ma_col(mashort)] - price_data[get_ma_col(malong)]
    price_data['DIFF_PREV'] = price_data.DIFF.shift(1)
    price_data['IS_TRADE'] = price_data.apply(is_trade, axis=1)
    
    df_trades = price_data[price_data.IS_TRADE!=0].copy()
    df_trades["DELTA"] = (df_trades.mid_c.diff() / i_pair.pipLocation).shift(-1)
    df_trades["GAIN"] = df_trades["DELTA"] * df_trades["IS_TRADE"]  

    df_trades["PAIR"] = i_pair.name
    df_trades["MASHORT"] = mashort
    df_trades["MALONG"] = malong

    del df_trades[get_ma_col(mashort)]
    del df_trades[get_ma_col(malong)]

    df_trades["time"] = [parse(x) for x in df_trades.time] 
    df_trades["DURATION"] = df_trades.time.diff().shift(-1)
    df_trades["DURATION"] = [x.total_seconds() / 3600 for x in df_trades.DURATION]
    df_trades.dropna(inplace=True)

    #print(f"{i_pair.name} {mashort} {malong} trades:{df_trades.shape[0]} gain:{df_trades['GAIN'].sum():.0f}")

    return ma_result.MAResult(
        df_trades=df_trades,
        pairname=i_pair.name,
        params={'mashort' : mashort, 'malong' : malong}
    )


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

def store_trades(results):
    all_trade_df_list = [x.df_trades for x in results]
    all_trade_df = pd.concat(all_trade_df_list)
    all_trade_df.to_pickle("all_trades.pkl")
    return all_trade_df

def process_results(results):
    results_list = [r.result_ob() for r in results]
    final_df = pd.DataFrame.from_dict(results_list)

    final_df.to_pickle('ma_test_res.pkl')
    print(final_df.shape, final_df.num_trades.sum())

    return final_df

def get_test_pairs(pair_str):
    existing_pairs = instrument.Instrument.get_instruments_dict().keys()
    pairs = pair_str.split(",")
    
    test_list = []
    for p1 in pairs:
        for p2 in pairs:
            p = f"{p1}_{p2}"
            if p in existing_pairs:
                test_list.append(p)
    
    print(test_list)
    return test_list

def run():
    currencies = "GBP,EUR,USD,CAD,JPY,NZD,CHF"
    granularity = "H1"
    ma_short = [4, 8, 16, 24, 32, 64]
    ma_long = [8, 16, 32, 64, 96, 128, 256]
    test_pairs = get_test_pairs(currencies)    

    results = []
    for pairname in test_pairs:
        print("running..", pairname)
        i_pair = instrument.Instrument.get_instruments_dict()[pairname]

        price_data = get_price_data(pairname, granularity)
        price_data = process_data(ma_short, ma_long, price_data)

        for _malong in ma_long:
            for _mashort in ma_short:
                if _mashort >= _malong:
                    continue
                results.append(evaluate_pair(i_pair, _mashort, _malong, price_data))

    final_df = process_results(results)
    all_trades_df = store_trades(results)

    create_excel(final_df, all_trades_df)


if __name__ == "__main__":
    run()