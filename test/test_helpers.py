from src.helpers import helpers
from src.evaluate_model import evaluate_model, ARIMAForecasting
import pandas as pd


def test_formatsql_sqlvar():
    test_sql = "SELECT artist FROM ${var:database} WHERE artist LIKE %Britney%"
    test_sqlvars = dict(database="Tracks")

    answer = "SELECT artist FROM Tracks WHERE artist LIKE %%Britney%%"

    assert helpers.format_sql(test_sql, replace_sqlvar=test_sqlvars) == answer


def test_evaluate_model():
    inputs = {
        'DATE': ['2019-05-01', '2019-05-02', '2019-05-03', '2019-05-06', '2019-05-07', '2019-05-08',
                 '2019-05-09', '2019-05-10', '2019-05-13', '2019-05-14', '2019-05-15', '2019-05-16'],
        'EUR': [0.88, 0.88, 0.90, 0.89, 0.91, 0.91, 0.92, 0.91, 0.91, 0.90, 0.91, 0.89],
        'GBP': [0.78, 0.81, 0.8, 0.79, ],
        'INR': [69.27, 69.30, 69.98, 69.56, 69.24, 69.11, 69.32, 69.41, 69.64, 69.83, 69.44, 69.22],
    }

    '''
    ARIMA_models = {
            'P': [1, 0, 0, 2, 0],
            'D': [1, 1, 1, 1, 1],
            'Q': [0, 0, 1, 0, 2]
        }
    '''
    time_slice_input = pd.DataFrame(data=inputs)

    expected = {
        'country' : ["India", "Italy", "Kenya"],
        'population': [np.nan, 400, 800],
        'total_area' : [100.23, 300.56, 700.5]
    }

    time_slice_output = pd.DataFrame(data=expected)
    time_slice_output = time_slice_output.set_index('country')

    # Check type
    assert isinstance(time_slice_output, pd.DataFrame)

    # Check expected output
    assert time_slice_output.equals(time_slice(time_slice_input, "2013-2017")[time_slice_output.columns])

