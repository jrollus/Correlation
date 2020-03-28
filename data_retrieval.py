import pandas as pd
import numpy as np
import pandas_datareader.data as web
from pandas_datareader._utils import RemoteDataError
from xbbg import blp


def get_relevant_data(tickers_list, date_start, date_end, data_source):
    """Get financial data from Yahoo Finance for a given set of underlying and type of data"""
    if data_source == 'Yahoo':
        try:
            raw_data = web.DataReader(name=tickers_list, data_source='yahoo', start=date_start, end=date_end)
            selected_data = raw_data['Adj Close']
        except RemoteDataError:
            selected_data = pd.DataFrame(np.nan, index=[0], columns=tickers_list)

    elif data_source == 'Bloomberg':
        selected_data = blp.bdh(tickers=tickers_list, flds=['PX_LAST'],
                                start_date=date_start, end_date=date_end, adjust='all')

        if not selected_data.empty:
            selected_data.columns = selected_data.columns.droplevel(1)

    return selected_data
