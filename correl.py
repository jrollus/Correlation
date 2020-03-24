import data_retrieval as dr
import correl_calc as cc
import plot_data as pl

# User inputs
tickers_list = ['TEF.MC', 'REP.MC', 'BBVA.MC']
time_windows = [250, 500]
data_to_plot = [('TEF.MC', 'REP.MC', 250), ('TEF.MC', 'REP.MC', 500), ('BASKET CORREL', 'BASKET CORREL', 250)]

# Get raw data
raw_data = dr.get_relevant_data(tickers_list, 'Adj Close')

# Process raw data
log_returns = cc.process_raw_data(raw_data)

# Compute pairwise correlations
corr_data = cc.get_pairwise_correlations(log_returns, time_windows)
avg_corr_data = cc.get_average_correlation(corr_data)

# Process corr data
cc.process_corr_data(corr_data, avg_corr_data)

# Output data to CSV
corr_data.to_csv('pairwise.csv', index=True)
avg_corr_data.to_csv('avg.csv', index=True)

# Plot
pl.plot_data(corr_data, avg_corr_data, data_to_plot)







