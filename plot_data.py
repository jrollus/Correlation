import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_data(corr_data, avg_corr_data, data_to_plot):
    """Function to plot data requested in MatplotLib"""
    idx = pd.IndexSlice
    plot_in_format = \
        pd.DataFrame(np.zeros(len(corr_data.index.unique('Date'))), index=corr_data.index.unique('Date'),
                     columns=[data_to_plot[0][0] + '/' + data_to_plot[0][1] + ' - ' + str(data_to_plot[0][2]) + 'D'])
    for data_series in data_to_plot:
        if data_series[0] != 'BASKET CORREL':
            plot_in_format[data_series[0] + '/' + data_series[1] + ' - ' + str(data_series[2]) + 'D'] = \
                corr_data.loc[idx[data_series[2], :, data_series[0]], data_series[1]].values
        else:
            plot_in_format[data_series[0] + ' - ' + str(data_series[2]) + 'D'] = \
                avg_corr_data.loc[idx[data_series[2], :], :].values

    # Plot Data
    ax = plot_in_format.plot(figsize=(15, 6), lw=2.)

    # General Parameters
    plt.title('Realized Correlation')
    plt.legend(loc=0)
    plt.grid(True)

    # X Axis
    plt.xlabel('Date')
    years = mdates.YearLocator()
    months = mdates.MonthLocator()
    years_fmt = mdates.DateFormatter('%Y')
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)
    ax.xaxis.set_minor_locator(months)

    # Y Axis
    plt.ylabel('Value')

    # Plot
    plt.show()
