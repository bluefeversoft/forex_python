import datetime as dt
from dateutil.parser import *

def time_utc():
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)

def get_utc_dt_from_string(date_str):
    d = parse(date_str)
    return d.replace(tzinfo=dt.timezone.utc)
