import gui as gu
from datetime import date, timedelta

# Main Code
input_parameter = gu.InputParameters(time_windows_input=[[10, 30, 50, 250, 500]], data_source='Yahoo',
                                     date_start=date.today() - timedelta(days=5*365),
                                     date_end=date.today() - timedelta(days=1))
input_parameter.configure_traits()

# # tickers_list = ['TEF.MC', 'REP.MC', 'BBVA.MC']
# # time_windows = [10, 20, 30, 50, 250, 500]
# #
# # data_source = 'Yahoo'
# # Get raw data
# raw_data = dr.get_relevant_data(tickers_list, 'Adj Close')
#
# # Process raw data
# log_returns = cc.process_raw_data(raw_data)
#
# # Compute pairwise correlations
# corr_data = cc.get_correlations(log_returns, time_windows)
#
# # Process corr data
# cc.process_corr_data(corr_data[0], corr_data[1])
#
# # Output data to CSV
# corr_data[0].to_csv('pairwise.csv', index=True)
# corr_data[1].to_csv('avg.csv', index=True)







# dt = np.dtype([('Und 1', 'S20'), ('Und 2', 'S20'), ('Time Window', 'i4')])
#     data_to_plot = trapi.Array(dtype=dt, shape=(100,3))




