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


def score_model(args):
    try:
        with open(config.MODEL_CONFIG, "r") as f:
            model_config = yaml.load(f)
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
    generate_predictions(rates, ARIMA_params, **load_config)


def generate_predictions(rates, ARIMA_params, FORECAST_PERIOD, **kwargs):

    predictions_INR = ARIMAForecasting(rates.INR, FORECAST_PERIOD,
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'INR', 'P'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'INR', 'D'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'INR', 'Q'].values[0])
    predictions_EUR = ARIMAForecasting(rates.EUR, FORECAST_PERIOD,
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'EUR', 'P'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'EUR', 'D'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'EUR', 'Q'].values[0])
    predictions_GBP = ARIMAForecasting(rates.GBP, FORECAST_PERIOD,
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'GBP', 'P'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'GBP', 'D'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'GBP', 'Q'].values[0])

    print(predictions_INR)
    print(predictions_GBP)
    print(predictions_EUR)
