import sys
import yaml
from datetime import datetime, timedelta
import pandas as pd
from src.evaluate_model import ARIMAForecasting
from src.load_data import load_ARIMA_Params
from src.helpers.helpers import invoke_api, get_engine
from src.create_dataset import create_Predictions
import config

import logging.config
logger = logging.getLogger(__name__)


def date_by_adding_business_days(from_date, add_days):
    """
    :param from_date: Date from which the next business date is to be found
    :param add_days: Number of business days that need to be added to from_date
    :return: The next business day after adding add_days to from_date (sat and sun are considered holidays)
    """
    business_days_to_add = add_days
    current_date = from_date
    try:
        while business_days_to_add > 0:
            current_date += timedelta(days=1)
            weekday = current_date.weekday()
            if weekday >= 5: # sunday = 6
                continue
            business_days_to_add -= 1
    except TypeError:
        logger.error("Non date type input received")
        sys.exit(1)

    return current_date


def generate_predictions(rates, ARIMA_params, FORECAST_PERIOD, **kwargs):
    """
    Generate predictions from the rates data and ARIMA parameters for the forecast period
    :param rates: The rates time series for INR, GBP and EUR
    :param ARIMA_params: The ARIMA parameters to be used for INR, GBP and EUR respectively
    :param FORECAST_PERIOD: Number of days for which the predictions are to be made
    :return:
    """

    predictions_df = pd.DataFrame(columns=['CURRENCY', 'PRED_DATE', 'PRED_RATE'])
    currencies = ['EUR', 'GBP', 'INR']

    try:
        now = datetime.strptime(rates['DATE'].iloc[-1], '%Y-%m-%d')

        for curr in currencies:
            predictions = ARIMAForecasting(rates[curr], FORECAST_PERIOD,
                                           ARIMA_params.loc[ARIMA_params['CURRENCY'] == curr, 'P'].values[0],
                                           ARIMA_params.loc[ARIMA_params['CURRENCY'] == curr, 'D'].values[0],
                                           ARIMA_params.loc[ARIMA_params['CURRENCY'] == curr, 'Q'].values[0])

            for i in range(FORECAST_PERIOD):
                next_dt = date_by_adding_business_days(now, (i+1))
                next_dt = next_dt.strftime("%Y-%m-%d")
                predictions_df = predictions_df.\
                    append({'CURRENCY': curr, 'PRED_DATE': next_dt, 'PRED_RATE': predictions[i]}, ignore_index=True)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    return predictions_df


def score_model(args):
    """
    Orchestrates the following functions:
    1. Construct the API URL from the configs set in the yaml
    2. Invoke the api and get latest exchange rates
    3. Load ARIMA parameters for best models
    4. Generate predictions
    5. Store predictions in the database
    """
    try:
        with open(config.MODEL_CONFIG, "r") as f:
            model_config = yaml.load(f, Loader=yaml.FullLoader)

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

        # Invoke the api and get latest exchange rates
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

    except Exception as e:
        logger.error(e)
        sys.exit(1)
        
    # Load model parameters
    engine = get_engine()
    ARIMA_params = load_ARIMA_Params(engine);

    # Generate predictions
    predictions_df = generate_predictions(rates, ARIMA_params, **load_config)

    # Store predictions in the database
    create_Predictions(engine, predictions_df)
    return
