import pandas as pd
import utils

class Instrument():
    def __init__(self, ob):
        self.name = ob['name']
        self.ins_type = ob['type']
        self.displayName = ob['displayName']
        self.pipLocation = pow(10, ob['pipLocation']) # -4 -> 0.0001
        self.marginRate = ob['marginRate']
        
    def __repr__(self):
        return str(vars(self))

    @classmethod
    def get_instruments_df(cls):
        return pd.read_pickle(utils.get_instruments_data_filename())

    @classmethod
    def get_instruments_list(cls):
        df = cls.get_instruments_df()
        return [Instrument(x) for x in df.to_dict(orient='records')]

    '''
    dict to access instruments by pair name

    instrument_dict =
    {
        "EUR_USD" : Instrument(),
        "EUR_GBP" : Instrument(),
        "..." : Instrument(),
    }

    our_instrument = instrument_dict["EUR_USD"]
    '''
    @classmethod
    def get_instruments_dict(cls):
        i_list = cls.get_instruments_list()
        i_keys = [x.name for x in i_list]
        return { k:v for (k,v) in zip(i_keys, i_list) }

    @classmethod
    def get_instrument_by_name(cls, pairname):
        d = cls.get_instruments_dict()
        if pairname in d:
            return d[pairname]
        else:
            return None

    @classmethod
    def get_pairs_from_string(cls, pair_str):
        existing_pairs = cls.get_instruments_dict().keys()
        pairs = pair_str.split(",")
        
        pair_list = []
        for p1 in pairs:
            for p2 in pairs:
                p = f"{p1}_{p2}"
                if p in existing_pairs:
                    pair_list.append(p)
        
        return pair_list

   

if __name__ == "__main__":
    print(Instrument.get_pairs_from_string("GBP,EUR,USD,CAD,JPY,NZD,CHF"))



