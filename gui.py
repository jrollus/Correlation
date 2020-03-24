import numpy as np
import traits.api as trapi
import traitsui.api as trui
import string as st
import data_retrieval as dr
import correl_calc as cc
import plot_data as pl

nbr_max_time_windows = 5


class InputParameters(trapi.HasTraits):
    """Class the is used to input all of the user parameters through a guy"""
    tickers_input = trapi.Str
    time_windows_input = trapi.Array(dtype=np.int, shape=(1, nbr_max_time_windows))
    data_source = trapi.Enum("Yahoo", "Bloomberg", "Telemaco")
    date_start = trapi.Date
    date_end = trapi.Date
    get_data_button = trapi.Button

    v = trui.View(trui.HGroup(
                            trui.Item(name='tickers_input', style='custom', ),
                            trui.VGroup(trui.Item(name='date_start'),
                                        trui.Item(name='date_end'),
                                        trui.Item(name='time_windows_input'),
                                        trui.Item(name='data_source'),
                                        trui.Item(name='get_data_button',
                                                  label='Process Data', show_label=False)),
                            show_border=True, label='Input Data'), resizable=True)

    def _get_data_button_fired(self):
        """Method to download the relevant data and then compute the relevant correlations"""
        tickers_list = self.tickers_input.strip().split()
        time_windows = self.time_windows_input[0, :]

        # Get raw data
        raw_data = dr.get_relevant_data(tickers_list, 'Adj Close')

        # Process raw data
        log_returns = cc.process_raw_data(raw_data)

        # Compute pairwise correlations
        corr_data = cc.get_correlations(log_returns, time_windows)

        # Process corr data
        cc.process_corr_data(corr_data[0], corr_data[1])

        # Output data to CSV
        corr_data[0].to_csv('pairwise.csv', index=True)
        corr_data[1].to_csv('avg.csv', index=True)

        # User inputs
        data_to_plot = [('TEF.MC', 'REP.MC', 250), ('TEF.MC', 'REP.MC', 500), ('BASKET CORREL', 'BASKET CORREL', 250)]

        # Plot
        pl.plot_data(corr_data[0], corr_data[1], data_to_plot)




