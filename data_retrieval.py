import pandas_datareader.data as web


def get_relevant_data(tickers_list, date_start, date_end, data_source):
    """Get financial data from Yahoo Finance for a given set of underlying and type of data"""
    if data_source == 'Yahoo':
        raw_data = web.DataReader(name=tickers_list, data_source='yahoo', start=date_start, end=date_end)
        selected_data = raw_data['Adj Close']
    return selected_data
