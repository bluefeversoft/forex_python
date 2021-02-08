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

def run_collection():
    pair_list = "GBP,EUR,USD,CAD,JPY,NZD,CHF"
    for g in INCREMENTS.keys():
        for i in Instrument.get_pairs_from_string(pair_list):
            print(g, i)

if __name__ == "__main__":
    run_collection()