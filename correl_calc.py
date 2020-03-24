import numpy as np
import pandas as pd


def process_corr_data(corr_data, avg_corr_data):
    """Remove dates where correlation could not be computed"""
    corr_data.dropna()
    avg_corr_data.dropna()


def process_raw_data(raw_data):
    """Function to remove line with empty data to ensure the data set is consistent and then compute log returns"""
    # Clear raw data
    raw_data.dropna()
    # Get log returns
    log_returns = np.log(raw_data / raw_data.shift(1))
    return log_returns


def get_pairwise_correlations(log_returns, time_windows):
    """Function to compute pairwise correlations given a DF of returns"""
    # Get tickers list
    tickers_list = log_returns.columns
    # Get DateIndex
    dates_index = log_returns.index
    # Define MultiIndex
    iterables = [time_windows, dates_index, tickers_list]
    multi_index = pd.MultiIndex.from_product(iterables, names=['Time Window', 'Date', 'Underlying'])
    multi_index_structure = np.zeros((len(tickers_list) * len(dates_index) * len(time_windows), len(tickers_list)))
    # Compute pairwise correlations
    for i in range(0, len(time_windows)):
        for j in range(0, len(tickers_list)):
            for k in range(j, len(tickers_list)):
                if j == k:
                    for l in range(0, len(dates_index)):
                        multi_index_structure[
                            (i * len(tickers_list) * len(dates_index)) + l * len(tickers_list) + j, k] = 1
                else:
                    corr = log_returns[log_returns.columns[j]].rolling(time_windows[i]). \
                        corr(log_returns[log_returns.columns[k]])
                    for l, (index, val) in enumerate(corr.iteritems()):
                        multi_index_structure[
                            (i * len(tickers_list) * len(dates_index)) + l * len(tickers_list) + j, k] = val
                        multi_index_structure[
                            (i * len(tickers_list) * len(dates_index)) + l * len(tickers_list) + k, j] = val

    return pd.DataFrame(multi_index_structure, index=multi_index, columns=tickers_list)


def get_average_correlation(corr_data):
    """Function to compute the average correlation for a given MultiIndex DataFrame, maintaining the structure"""
    # Extract the first two levels of the DataFrame
    time_windows = corr_data.index.unique('Time Window')
    dates_index = corr_data.index.unique('Date')
    # Generate the MultiIndex
    iterables = [time_windows, dates_index]
    multi_index = pd.MultiIndex.from_product(iterables, names=['Time Window', 'Date'])
    multi_index_structure = np.zeros((len(dates_index) * len(time_windows), 1))
    # Compute average basket correlation
    for i in range(0, len(time_windows)):
        for j in range(0, len(dates_index)):
            multi_index_structure[i * len(dates_index) + j, 0] = \
                corr_data.loc[(time_windows[i], dates_index[j])].values[np.triu_indices_from(corr_data.loc[(time_windows[i], dates_index[j])].values, 1)].mean()

    return pd.DataFrame(multi_index_structure, index=multi_index, columns=['Avg Correl'])