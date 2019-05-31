import sys
import yaml
from datetime import datetime, timedelta
import pandas as pd
from src.evaluate_model import ARIMAForecasting
from src.load_data import load_ARIMA_Params
from src.helpers.helpers import invoke_api
import config

import logging.config
logger = logging.getLogger(__name__)


def date_by_adding_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5: # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date


def generate_predictions(rates, ARIMA_params, FORECAST_PERIOD, **kwargs):
    """ Generate predictions from the rate data and ARIMA parameters for the forecast period"""

    predictions_df = pd.DataFrame(columns=['currrency', 'date', 'rate'])
    currencies = ['INR', 'GBP', 'EUR']
    now = datetime.now()

    for curr in currencies:
        predictions = ARIMAForecasting(rates[curr], FORECAST_PERIOD,
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == curr, 'P'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == curr, 'D'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == curr, 'Q'].values[0])

        for i in range(FORECAST_PERIOD):
            next_dt = date_by_adding_business_days(now, (i+1))
            next_dt = next_dt.strftime("%Y-%m-%d")
            predictions_df = predictions_df.\
                append({'currrency': curr, 'date': next_dt, 'rate': predictions[i]}, ignore_index=True)

    print(predictions_df)
    return predictions_df


def score_model(args):
    """ Load the best model parameters and fetch the latest rate data to generate predictions"""
    try:
        with open(config.MODEL_CONFIG, "r") as f:
            model_config = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logger.error("YAML not found")
        sys.exit(1)

    load_config = model_config["score_model"]
    now = datetime.now()
    end_date = now.strftime("%Y-%m-%d")
    start_date = now - timedelta(days = load_config["NUM_LOOK_BACK_YRS"] * 365)
    start_date = start_date.strftime("%Y-%m-%d")

    # Construct the API URL from the configs set in the yaml
    base_url = load_config["BASE_URL"]
    api_url = "{base_url}?start_at={start_date}&end_at={end_date}&base=USD"
    api_url = api_url.format(base_url=base_url, start_date=start_date,
                             end_date=end_date)

    data = invoke_api(api_url)

    dates_list = list(data['rates'].keys())
    inputs = {
        'DATE': [date for date in dates_list],
        'EUR': [data['rates'][date]['EUR'] for date in dates_list],
        'INR': [data['rates'][date]['INR'] for date in dates_list],
        'GBP': [data['rates'][date]['GBP'] for date in dates_list]
    }

    rates = pd.DataFrame(data=inputs)
    rates = rates.sort_values(by=['DATE'], ascending=True).reset_index(drop=True)

    ARIMA_params = load_ARIMA_Params(args);
    predictions_df = generate_predictions(rates, ARIMA_params, **load_config)
    return
