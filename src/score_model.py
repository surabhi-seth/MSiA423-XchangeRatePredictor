from datetime import datetime, timedelta
from src.load_data import load_Rates, load_ARIMAParams
from src.train_model import ARIMAForecasting
from . import NUM_LOOK_BACK_YRS, FORECAST_PERIOD


def score_model():
    now = datetime.now()
    end_date = now.strftime("%Y-%m-%d")
    start_date = now - timedelta(days = NUM_LOOK_BACK_YRS * 365)
    start_date = start_date.strftime("%Y-%m-%d")

    # Use last 3 year's data to make predictions
    historic_rates = load_Rates();
    historic_rates = historic_rates.loc[(historic_rates['DATE'] > start_date) &
                                        (historic_rates['DATE'] <= end_date)].reset_index(drop=True)

    ARIMA_params = load_ARIMAParams();

    predictions_INR = ARIMAForecasting(historic_rates.INR[0:len(historic_rates.INR) - FORECAST_PERIOD],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'INR', 'P'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'INR', 'D'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'INR', 'Q'].values[0])
    predictions_EUR = ARIMAForecasting(historic_rates.EUR[0:len(historic_rates.EUR) - FORECAST_PERIOD],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'EUR', 'P'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'EUR', 'D'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'EUR', 'Q'].values[0])
    predictions_GBP = ARIMAForecasting(historic_rates.GBP[0:len(historic_rates.GBP) - FORECAST_PERIOD],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'GBP', 'P'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'GBP', 'D'].values[0],
                                       ARIMA_params.loc[ARIMA_params['CURRENCY'] == 'GBP', 'Q'].values[0])

    print(predictions_INR)
    print(predictions_GBP)
    print(predictions_EUR)
