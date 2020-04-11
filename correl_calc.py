import numpy as np
import pandas as pd
import sqlite3 as sq3
import datetime as dt
from pandas.tseries.offsets import BDay


def process_corr_data(corr_data, avg_corr_data):
    """Export computed correlations to .csv"""
    # Output data to CSV
    corr_data.to_csv('pairwise.csv', index=True)
    avg_corr_data.to_csv('avg.csv', index=True)


def process_raw_data(raw_data):
    """Function to remove line with empty data to ensure the data set is consistent and then compute log returns"""
    # Clear raw data
    raw_data = raw_data.dropna()
    # Get log returns
    log_returns = np.log(raw_data / raw_data.shift(1))
    return log_returns.dropna()


def get_correlations(log_returns, time_windows):
    """Function to compute pairwise correlations given a DF of returns"""
    # Get tickers list
    tickers_list = log_returns.columns
    nbr_pairwise_corr = int((len(tickers_list) * (len(tickers_list) - 1)) / 2)
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


def filter_log_returns(log_returns):
    """Function to filter log returns and remove extraordinary days that do no fall within a 1 day window from
    a result date"""
    # Parameters
    filtering_moving_window = 3
    max_normal_day_std_dev = 4
    max_normal_day_return = 0.06
    max_result_day_std_dev = 2
    max_result_day_return = 0.15
    path = ''

    # Get tickers list
    tickers_list = log_returns.columns
    # Get DateIndex
    dates_index = log_returns.index
    iterables = [tickers_list, ['Mean', 'Std. Dev']]
    multi_index_columns = pd.MultiIndex.from_product(iterables, names=['Underlying', 'Stats'])
    multi_index_structure = np.zeros((len(dates_index),len(tickers_list)*2))
    # Compute rolling stats for normal days
    und_counter = 0
    for i in range(0, len(tickers_list)):
        multi_index_structure[:, i + und_counter] = \
            log_returns[log_returns.columns[i]].rolling(filtering_moving_window).mean().shift().values
        multi_index_structure[:, i + 1 + und_counter] =\
            log_returns[log_returns.columns[i]].rolling(filtering_moving_window).std().shift().values
        und_counter += 1

    normal_days_stats = pd.DataFrame(multi_index_structure, index=dates_index, columns=multi_index_columns)

    # Get result dates from database
    query = 'SELECT * FROM t_results'
    con = sq3.connect(path + 'Correl_Params.s3db')
    raw_result_dates_data = pd.read_sql_query(query, con)
    raw_result_dates_data['date_result'] = pd.TimedeltaIndex(raw_result_dates_data['date_result'], unit='d') +\
                                           dt.datetime(1899, 12, 30) # Convert Excel integer date to Pandas date

    # Filtering process
    idx = pd.IndexSlice
    for i in range(0, len(tickers_list)):
        # Retrieve result dates from the DB and generate the dates that are 1 BD after as well
        dates_vector = raw_result_dates_data.loc[raw_result_dates_data['bbg'] == tickers_list[i], 'date_result']
        dates_vector = dates_vector.append(dates_vector.apply(lambda x: x + BDay(1)))
        # On the the dates that don't fall within the extended result dates vector generated above, apply the filter
        std_dev_vector = (abs(normal_days_stats.loc[:, idx[tickers_list[i], 'Mean']]) +
                        max_normal_day_std_dev * normal_days_stats.loc[:, idx[tickers_list[i], 'Std. Dev']])
        std_dev_vector.loc[std_dev_vector < max_normal_day_return] = max_normal_day_return
        log_returns.loc[
            (log_returns.index.isin(dates_vector) == False) & (abs(log_returns[tickers_list[i]]) >= std_dev_vector),
            tickers_list[i]] = np.nan
        # On the the dates that do fall within the extended result dates vector generated above, apply the filter
        result_dates_avg = log_returns.loc[log_returns.index.isin(dates_vector), tickers_list[i]].mean()
        result_dates_std_dev = log_returns.loc[log_returns.index.isin(dates_vector), tickers_list[i]].std()
        result_dates_cap = \
            min(max_result_day_return, abs(result_dates_avg) + max_result_day_std_dev * result_dates_std_dev)
        log_returns.loc[
            (log_returns.index.isin(dates_vector)) & (abs(log_returns[tickers_list[i]]) >= result_dates_cap),
            tickers_list[i]] = result_dates_cap

    log_returns = log_returns.dropna()

    return log_returns

