import numpy as np
import pandas as pd
import traits.api as trapi
import traitsui.api as trui
import itertools as it
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn

import data_retrieval as dr
import correl_calc as cc
import plot_data as pl

nbr_max_time_windows = 5
screen_height = 400
screen_width = 600
# message_height = 100
# message_width = 320

# The 'correlpairs' trait table editor:
correl_pair_editor = trui.TableEditor(
    sortable=False,
    configurable=False,
    auto_size=False,
    selected_indices='selected_correl_pair_indices',
    columns=[ObjectColumn(name='correl_pair', label='Correlation Pair / Time Window',
                          horizontal_alignment='center', width=0.24),
             CheckboxColumn(name='time_window_1', label='', horizontal_alignment='center', width=0.08),
             CheckboxColumn(name='time_window_2', label='', horizontal_alignment='center', width=0.08),
             CheckboxColumn(name='time_window_3', label='', horizontal_alignment='center', width=0.08),
             CheckboxColumn(name='time_window_4', label='', horizontal_alignment='center', width=0.08),
             CheckboxColumn(name='time_window_5', label='', horizontal_alignment='center', width=0.08,
                            editable=True, format='%0.3f')])


class Message(trapi.HasPrivateTraits):
    """A class to show a message to the user"""
    message = trapi.Str


def message(message_input="", parent=None):
    """Displays a message to the user as a model window"""
    msg = Message(message=message_input)
    ui = msg.edit_traits(
        parent=parent,
        view=trui.View(
            ["message~", "|<>"], title='Error', buttons=["OK"], kind="modal", resizable=True,
            icon='corr.png', image='corr.png'
        ),
    )
    return ui.result


class InputParameter(trapi.HasTraits):
    """Class the is used to input all of the user parameters through a guy"""
    tickers_input = trapi.Str
    time_windows_input = trapi.Array(trapi.Int, (1, nbr_max_time_windows))
    data_source = trapi.Enum("Yahoo", "Bloomberg", "Telemaco")
    date_start = trapi.Date
    date_end = trapi.Date
    get_data_button = trapi.Button
    plot_chart_button = trapi.Button
    correlpairs = trapi.List
    selected_correl_pair_indices = trapi.List
    corr_pairs_combinations = trapi.List
    v = trui.View(trui.HGroup(
        trui.Item(name='tickers_input', style='custom'),
        trui.VGroup(trui.Item(name='date_start'),
                    trui.Item(name='date_end'),
                    trui.Item(name='time_windows_input'),
                    trui.Item(name='data_source'),
                    trui.Item(name='get_data_button',
                              label='Process Data', show_label=False),
                    trui.Item('correlpairs', show_label=False, editor=correl_pair_editor),
                    trui.Item(name='plot_chart_button',
                              label='Plot Selected Data', show_label=False),
                    ),
        show_border=True, label='Input Data'), resizable=True, title='Correlation Tool',
        height=screen_height, width=screen_width, icon='corr.png', image='corr.png')

    def _plot_chart_button_fired(self):
        """Method to plot the selected data"""
        # Read data from CSV
        corr_data = [pd.read_csv('pairwise.csv', index_col=[0, 1, 2]), pd.read_csv('avg.csv', index_col=[0, 1])]

        # Read TableEditor to see what the user has chosen to
        data_to_plot = []
        for i in range(0, len(self.correlpairs)):
            if i == len(self.correlpairs)-1:
                pair_name = ['BASKET CORREL', 'BASKET CORREL']
            else:
                pair_name = self.correlpairs[i].correl_pair.split('-')

            if self.correlpairs[i].time_window_1:
                data_to_plot.append((pair_name[0].strip(), pair_name[1].strip(), self.time_windows_input[0][0]))
            if self.correlpairs[i].time_window_2:
                data_to_plot.append((pair_name[0].strip(), pair_name[1].strip(), self.time_windows_input[0][1]))
            if self.correlpairs[i].time_window_3:
                data_to_plot.append((pair_name[0].strip(), pair_name[1].strip(), self.time_windows_input[0][2]))
            if self.correlpairs[i].time_window_4:
                data_to_plot.append((pair_name[0].strip(), pair_name[1].strip(), self.time_windows_input[0][3]))
            if self.correlpairs[i].time_window_5:
                data_to_plot.append((pair_name[0].strip(), pair_name[1].strip(), self.time_windows_input[0][4]))

        # Plot
        pl.plot_data(corr_data[0], corr_data[1], data_to_plot)

    def check_data_retrieval_error(self, raw_data, tickers_list):
        """Check whether there was an error retrieving data"""
        # Check whether data was retrieved successfully:
        if self.data_source == 'Yahoo':
            if len(tickers_list) > 1:
                empty_col = []
                for column_name in raw_data.columns:
                    if raw_data[column_name].isna().all():
                        empty_col.append(column_name)
                        raw_data[column_name].drop
                if empty_col:
                    message('There was a problem loading data for the following underlyings:\n' + '\n'.join(empty_col))
                    return [x for x in tickers_list if x not in empty_col]
            else:
                return tickers_list

        elif self.data_source == 'Bloomberg':
            if len(tickers_list) > 1:
                if len(raw_data.columns) < len(tickers_list):
                    und_errors = np.setdiff1d(tickers_list, raw_data.columns)
                    message('There was a problem loading data for the following underlyings:\n' + '\n'.join(und_errors))
                    return [x for x in tickers_list if x not in und_errors]
            else:
                return tickers_list

    def _get_data_button_fired(self):
        """Method to download the relevant data and then compute the relevant correlations"""
        tickers_list = self.tickers_input.strip().split('\n')

        time_windows = self.time_windows_input[0, :].astype(int)

        # Get raw data
        raw_data = dr.get_relevant_data(tickers_list, self.date_start, self.date_end, self.data_source)

        # Check whether there was an error retrieving data
        tickers_list = self.check_data_retrieval_error(raw_data, tickers_list)
        if len(tickers_list) <= 1:
            message('You need at least two underlyings to compute correlations')
            return

        # Process raw data
        log_returns = cc.process_raw_data(raw_data)

        # Compute pairwise correlations
        corr_data = cc.get_correlations(log_returns, time_windows)

        # Process corr data
        cc.process_corr_data(corr_data[0], corr_data[1])

        # Output data to CSV
        corr_data[0].to_csv('pairwise.csv', index=True)
        corr_data[1].to_csv('avg.csv', index=True)

        # Generate TableEditor
        for i in range(0,len(time_windows)):
            correl_pair_editor.columns[i+1].label = str(time_windows[i])
        self.corr_pairs_combinations = [pair[0] + ' - ' + pair[1] for pair in it.combinations(tickers_list, 2)]
        self.corr_pairs_combinations.append('BASKET CORREL')
        self.correlpairs = [generate_correl_pair(pair) for pair in self.corr_pairs_combinations]


class CorrelPair(trapi.HasStrictTraits):
    """Class to define a row in the table"""
    # Trait definitions:
    correl_pair = trapi.Str
    time_window_1 = trapi.Bool
    time_window_2 = trapi.Bool
    time_window_3 = trapi.Bool
    time_window_4 = trapi.Bool
    time_window_5 = trapi.Bool


def generate_correl_pair(c_pair):
    """Generates a CorrelPair"""
    cp = CorrelPair(correl_pair=c_pair,
                    time_window_1=False,
                    time_window_2=False,
                    time_window_3=False,
                    time_window_4=False,
                    time_window_5=False,
                    )
    return cp.trait_set()
