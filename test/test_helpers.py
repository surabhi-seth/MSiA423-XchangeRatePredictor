from src.helpers import helpers
from src.train_model import find_best_model
from src.evaluate_model import evaluate_model, ARIMAForecasting
from src.score_model import date_by_adding_business_days, generate_predictions
import pandas as pd
from pandas.util.testing import assert_frame_equal
from datetime import datetime


def test_evaluate_model():
    inputs = {
        'DATE': ['2019-05-01', '2019-05-02', '2019-05-03', '2019-05-06', '2019-05-07', '2019-05-08',
                 '2019-05-09', '2019-05-10', '2019-05-13', '2019-05-14', '2019-05-15', '2019-05-16'],
        'EUR': [0.88, 0.88, 0.90, 0.89, 0.91, 0.91, 0.92, 0.91, 0.91, 0.90, 0.91, 0.89],
        'GBP': [0.78, 0.81, 0.8, 0.79, 0.795, 0.798, 0.785, 0.777, 0.782, 0.788, 0.804, 0.79],
        'INR': [69.27, 69.30, 69.98, 69.56, 69.24, 69.11, 69.32, 69.41, 69.64, 69.83, 69.44, 69.22],
    }
    rates = pd.DataFrame(data=inputs)

    ARIMA_models = {
            'P': [1, 0, 0, 2, 0],
            'D': [1, 1, 1, 1, 1],
            'Q': [0, 0, 1, 0, 2]
        }
    forecast_period = 3

    expected = {
        'P': [1, 0, 0, 2, 0],
        'D': [1, 1, 1, 1, 1],
        'Q': [0, 0, 1, 0, 2],
        'MAPE_INR': [0.469204, 0.477241, 0.370169, 0.245564, 0.355792],
        'MAPE_EUR': [2.281700, 1.944444, 3.387799, 0.620243, 1.302068],
        'MAPE_GBP': [2.549810, 1.448363, 1.751258, 2.291886, 0.701285]
    }
    expected_output = pd.DataFrame(data=expected)

    actual_result = evaluate_model(rates, forecast_period, ARIMA_models)[expected_output.columns]
    # Check type
    assert isinstance(expected_output, pd.DataFrame)

    # Check expected output
    assert_frame_equal(expected_output, actual_result)


def test_ARIMAForecasting():
    inputs = [69.27, 69.30, 69.98, 69.56, 69.24, 69.11, 69.32, 69.41, 69.64, 69.83, 69.44, 69.22]
    actual_result = pd.DataFrame(ARIMAForecasting(inputs, 7, 2, 1, 0))

    expected = [69.29750101, 69.30063652, 69.21203591, 69.15348727, 69.12276635, 69.08049773, 69.02994465]
    expected_output = pd.DataFrame(data=expected)

    # Check expected output
    assert_frame_equal(expected_output, actual_result)


def test_find_best_model():
    inputs = {
        'P': [1, 0, 0, 2, 0],
        'D': [1, 1, 1, 1, 1],
        'Q': [0, 0, 1, 0, 2],
        'MAPE_INR': [0.469204, 0.477241, 0.370169, 0.245564, 0.355792],
        'MAPE_EUR': [2.281700, 1.944444, 3.387799, 0.620243, 1.302068],
        'MAPE_GBP': [2.549810, 1.448363, 1.751258, 2.291886, 0.701285]
    }
    models = pd.DataFrame(data=inputs)
    actual_result = find_best_model(models)

    expected = {
        'CURRENCY': ['EUR', 'GBP', 'INR'],
        'P': [2, 0, 2],
        'D': [1, 1, 1],
        'Q': [0, 2, 0],
        'MAPE': [0.620243, 0.701285, 0.245564]
    }
    expected_output = pd.DataFrame(data=expected)

    assert_frame_equal(expected_output, actual_result, check_dtype=False)



def test_date_by_adding_business_days_1():
    # Find 2 days from a Thursday - Result should be the next Monday
    input_date = datetime.strptime('2019-06-06', '%Y-%m-%d')
    actual_result = date_by_adding_business_days(input_date, 2).strftime("%Y-%m-%d")

    expected_output = '2019-06-10'
    assert actual_result == expected_output


def test_date_by_adding_business_days_2():
    # Find 2 days from a Saturday - Result should be the next Tuesday
    input_date = datetime.strptime('2019-06-08', '%Y-%m-%d')
    actual_result = date_by_adding_business_days(input_date, 2).strftime("%Y-%m-%d")

    expected_output = '2019-06-11'
    assert actual_result == expected_output


def test_generate_predictions():
    inputs = {
        'DATE': ['2019-05-22', '2019-05-23', '2019-05-24', '2019-05-27', '2019-05-28', '2019-05-29',
                 '2019-05-30', '2019-05-31', '2019-06-03', '2019-06-04', '2019-06-05', '2019-06-06'],
        'EUR': [0.88, 0.88, 0.90, 0.89, 0.91, 0.91, 0.92, 0.91, 0.91, 0.90, 0.91, 0.89],
        'GBP': [0.78, 0.81, 0.8, 0.79, 0.795, 0.798, 0.785, 0.777, 0.782, 0.788, 0.804, 0.79],
        'INR': [69.27, 69.30, 69.98, 69.56, 69.24, 69.11, 69.32, 69.41, 69.64, 69.83, 69.44, 69.22],
    }
    rates = pd.DataFrame(data=inputs)

    params = {
        'CURRENCY': ['EUR', 'GBP', 'INR'],
        'P': [2, 0, 2],
        'D': [1, 1, 1],
        'Q': [0, 2, 0],
        'MAPE': [0.620243, 0.701285, 0.245564]
    }
    ARIMA_params = pd.DataFrame(data=params)

    forecast_period = 7
    actual_result = generate_predictions(rates, ARIMA_params, forecast_period)

    expected = {
        'CURRENCY': ['EUR', 'EUR', 'EUR', 'EUR', 'EUR', 'EUR', 'EUR',
                     'GBP', 'GBP', 'GBP', 'GBP', 'GBP', 'GBP', 'GBP',
                     'INR', 'INR', 'INR', 'INR', 'INR', 'INR', 'INR'],
        'PRED_DATE': ['2019-06-07', '2019-06-10', '2019-06-11', '2019-06-12', '2019-06-13', '2019-06-14', '2019-06-17',
                      '2019-06-07', '2019-06-10', '2019-06-11', '2019-06-12', '2019-06-13', '2019-06-14', '2019-06-17',
                      '2019-06-07', '2019-06-10', '2019-06-11', '2019-06-12', '2019-06-13', '2019-06-14', '2019-06-17'],
        'PRED_RATE': [0.90051886, 0.88329409, 0.89334237, 0.87800716, 0.88721431, 0.87331546, 0.88157766,
                      0.78948845, 0.79638579, 0.79764623, 0.79890668, 0.80016712, 0.80142757, 0.80268801,
                      69.29750101, 69.30063652, 69.21203591, 69.15348727, 69.12276635, 69.08049773, 69.02994465]
    }
    expected_output = pd.DataFrame(data=expected)

    assert_frame_equal(expected_output, actual_result)