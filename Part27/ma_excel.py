import pandas as pd
import xlsxwriter

def add_pair_sheets(ma_test_res, writer):

    for p in ma_test_res.pair.unique():
        temp_df = ma_test_res[ma_test_res.pair==p]
        temp_df.to_excel(writer, sheet_name=p, index=False)

def create_excel(ma_test_res):
    filename = "ma_results.xlsx"
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    ma_test_res = ma_test_res[['pair', 'num_trades', 'total_gain','mashort', 'malong']].copy()
    ma_test_res["CROSS"] = "MA_" + ma_test_res.mashort.map(str) + "_" + ma_test_res.malong.map(str)

    ma_test_res.sort_values(by=["pair", "total_gain"], ascending=[True,False], inplace=True)

    add_pair_sheets(ma_test_res, writer)

    writer.save()


if __name__ == "__main__":
    df = pd.read_pickle("ma_test_res.pkl")
    create_excel(df)