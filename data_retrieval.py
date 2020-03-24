import pandas_datareader.data as web


def get_relevant_data(tickers_list, data_type):
    """Get financial data from Yahoo Finance for a given set of underlying and type of data"""
    raw_data = web.DataReader(name=tickers_list, data_source='yahoo', start='2000-1-1')
    selected_data = raw_data[data_type]
    return selected_data
