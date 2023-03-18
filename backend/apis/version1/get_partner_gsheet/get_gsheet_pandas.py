# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 15:40:23 2023

@author: dludwinski
"""

import pandas as pd
from numpy import array

SPREADSHEET_ID = '1jTxFZn8H3GsQK8kqIM9677WZcU3kVwSwj7LQHM5Q88Y'


def pandas_read_google_sheet(wbook_id=SPREADSHEET_ID) -> pd.DataFrame:
    """
    Return Pandas DataFrame with Daily Deals Google Sheets.

    Parameters
    ----------
    wbook_id : str
        String from url identifying google sheets workbook

    Returns
    -------
    pd.DataFrame(columns=['name', 'phone', 'Daily Deal', 'Promo Code'])

    """
    return pd.read_csv(
        f'https://docs.google.com/spreadsheets/d/{wbook_id}/export?format=csv&gid=0',
    ).dropna(axis=1).set_index('name')


def _get_number_of_deals(df: pd.DataFrame) -> int:
    return len(df)


def _get_all_company_names(df: pd.DataFrame) -> pd.DataFrame:
    return [name for name in df.index.unique()]


def _get_all_col_values(df: pd.DataFrame) -> list:
    return df.values


def _get_company_info_dict(vals_array: array) -> dict:
    return {
        'Contact': vals_array[0][0],
        'Address': vals_array[0][1],
        'A Cult Favorite': vals_array[0][2],
        'Specials': vals_array[0][3],
        'Image': vals_array[0][4],
        }


def _get_deal_workbook_and_return_dict() -> dict:
    deals_gsheet = pandas_read_google_sheet()
    deals_df = deals_gsheet.copy().fillna(' ')
    co_names_list = _get_all_company_names(deals_df)
    deals_dict = {}
    for co in co_names_list:
        co_df = deals_df.loc[deals_df.index.str.contains(co)]
        co_vals = _get_all_col_values(co_df)
        deals_dict[co] = _get_company_info_dict(co_vals)
    return deals_dict


if __name__ == '__main__':
    data = _get_deal_workbook_and_return_dict()
    for key, value in data.items():
        print(key)
        for k, v in value.items():
            print(k)
            print(v)
            print()
