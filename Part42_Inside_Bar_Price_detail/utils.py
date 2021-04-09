import datetime as dt
from dateutil.parser import *

def get_his_data_filename(pair, granularity):
    return f"his_data/{pair}_{granularity}.pkl"

def get_instruments_data_filename():
    return "instruments.pkl"

def time_utc():
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)

def get_utc_dt_from_string(date_str):
    d = parse(date_str)
    return d.replace(tzinfo=dt.timezone.utc)

if __name__ == "__main__":
    #print(get_his_data_filename("EUR_USD", "H1"))
    #print(get_instruments_data_filename())
    print(dt.datetime.utcnow())
    print(time_utc())
    print(get_utc_dt_from_string("2020-02-01 03:00:00"))