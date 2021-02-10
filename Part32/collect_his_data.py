import pandas as pd
import datetime as dt

from instrument import Instrument
import utils
from oanda_api import OandaAPI

INCREMENTS = {
    'M5' : 5,
    'H1' : 60,
    'H4' : 240
}


def create_file(pair, granularity, api):
    candle_count = 2000
    time_step = INCREMENTS[granularity] * candle_count

    end_date = utils.get_utc_dt_from_string("2020-12-31 23:59:59")
    date_from = utils.get_utc_dt_from_string("2018-01-01 00:00:00")

    candle_dfs = []

    date_to = date_from
    while date_to < end_date:
        date_to = date_from + dt.timedelta(minutes=time_step)
        if date_to > end_date:
            date_to = end_date
                
        date_from = date_to


def run_collection():
    pair_list = "GBP,EUR,USD,CAD,JPY,NZD,CHF"
    for g in INCREMENTS.keys():
        for i in Instrument.get_pairs_from_string(pair_list):
            create_file(i, g, api)

if __name__ == "__main__":
    run_collection()