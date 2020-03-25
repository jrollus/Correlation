import gui as gu
from datetime import date, timedelta

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    input_parameters = gu.InputParameter(time_windows_input=[[10, 30, 50, 250, 500]], data_source='Yahoo',
                                         date_start=date.today() - timedelta(days=5*365),
                                         date_end=date.today() - timedelta(days=1))
    input_parameters.configure_traits()




