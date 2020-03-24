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


def get_correlations(log_returns, time_windows):
    """Function to compute pairwise correlations given a DF of returns"""
    # Get tickers list
    tickers_list = log_returns.columns
    nbr_pairwise_corr = int((len(tickers_list) * (len(tickers_list)-1))/2)
    # Get DateIndex
    dates_index = log_returns.index
    # Define MultiIndex for pairwise correlations
    iterables = [time_windows, dates_index, tickers_list]
    multi_index_pair_wise = pd.MultiIndex.from_product(iterables, names=['Time Window', 'Date', 'Underlying'])
    multi_index_structure_pairwise = \
        np.zeros((len(tickers_list) * len(dates_index) * len(time_windows), len(tickers_list)))
    # Define MultiIndex for average correlations
    iterables = [time_windows, dates_index]
    multi_index_avg = pd.MultiIndex.from_product(iterables, names=['Time Window', 'Date'])
    multi_index_structure_avg = np.zeros((len(dates_index) * len(time_windows)))
    # Compute pairwise correlations
    for i in range(0, len(time_windows)):
        # Variable to hold different rolling pairwise correlation vectors in order to compute average correlation
        pairwise_correl_matrix = np.zeros((len(dates_index), nbr_pairwise_corr))
        pair_counter = 0
        for j in range(0, len(tickers_list)):
            for k in range(j, len(tickers_list)):
                if j == k:
                    for l in range(0, len(dates_index)):
                        multi_index_structure_pairwise[
                            (i * len(tickers_list) * len(dates_index)) + l * len(tickers_list) + j, k] = 1
                else:
                    corr = log_returns[log_returns.columns[j]].rolling(time_windows[i]). \
                        corr(log_returns[log_returns.columns[k]])
                    # Store data in a NumPy array
                    pairwise_correl_matrix[:, pair_counter] = corr.values
                    pair_counter += 1
                    for l, (index, val) in enumerate(corr.iteritems()):
                        multi_index_structure_pairwise[
                            (i * len(tickers_list) * len(dates_index)) + l * len(tickers_list) + j, k] = val
                        multi_index_structure_pairwise[
                            (i * len(tickers_list) * len(dates_index)) + l * len(tickers_list) + k, j] = val
            # On the last iteration (i.e. all pairwise correlation have been computed, get average correlation
            if j == len(tickers_list) - 1:
                multi_index_structure_avg[i * len(dates_index):((i + 1) * len(dates_index))] = \
                    np.mean(pairwise_correl_matrix, axis=1)

    return pd.DataFrame(multi_index_structure_pairwise, index=multi_index_pair_wise, columns=tickers_list),\
           pd.DataFrame(multi_index_structure_avg, index=multi_index_avg, columns=['Avg Correl'])