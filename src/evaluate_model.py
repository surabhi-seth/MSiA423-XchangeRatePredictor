from src import END_DATE
from src.load_data import load_Rates
from src.train_model import ARIMAForecasting
from src.create_dataset import create_ARIMAParams
from . import FORECAST_PERIOD
import pandas as pd

ARIMA_models = {
        'P': [1, 0, 0, 2, 0],
        'D': [1, 1, 1, 1, 1],
        'Q': [0, 0, 1, 0, 2]
    }


def evaluate_model():
    rates = load_Rates()
    rates = rates.loc[rates['DATE'] <= END_DATE]
    models = pd.DataFrame(data=ARIMA_models)
    MAPE_INR = []
    MAPE_EUR = []
    MAPE_GBP = []

    for i in range(len(ARIMA_models['P'])):
        predictions_INR = ARIMAForecasting(rates.INR[0:len(rates.INR) - FORECAST_PERIOD],
                                           ARIMA_models['P'][i], ARIMA_models['D'][i], ARIMA_models['Q'][i])
        MAPE_INR.append(sum(abs(predictions_INR - rates.INR[len(rates.INR) - FORECAST_PERIOD:len(rates.INR)])) / \
                            sum(rates.INR[len(rates.INR) - FORECAST_PERIOD:len(rates.INR)]))

        predictions_EUR = ARIMAForecasting(rates.EUR[0:len(rates.EUR) - FORECAST_PERIOD],
                                           ARIMA_models['P'][i], ARIMA_models['D'][i], ARIMA_models['Q'][i])
        MAPE_EUR.append(sum(abs(predictions_EUR - rates.EUR[len(rates.EUR) - FORECAST_PERIOD:len(rates.EUR)])) / \
                        sum(rates.EUR[len(rates.EUR) - FORECAST_PERIOD:len(rates.EUR)]))

        predictions_GBP = ARIMAForecasting(rates.GBP[0:len(rates.GBP) - FORECAST_PERIOD],
                                           ARIMA_models['P'][i], ARIMA_models['D'][i], ARIMA_models['Q'][i])
        MAPE_GBP.append(sum(abs(predictions_GBP - rates.GBP[len(rates.GBP) - FORECAST_PERIOD:len(rates.GBP)])) / \
                        sum(rates.GBP[len(rates.GBP) - FORECAST_PERIOD:len(rates.GBP)]))

    #Append the MAPE values to the different models
    models['MAPE_INR'] = MAPE_INR
    models['MAPE_EUR'] = MAPE_EUR
    models['MAPE_GBP'] = MAPE_GBP
    #print(models)

    #Insert the p,d,q values for the best ARIMA model
    create_ARIMAParams("INR", models.loc[models['MAPE_INR'].idxmin()].P,
                        models.loc[models['MAPE_INR'].idxmin()].D, models.loc[models['MAPE_INR'].idxmin()].Q)
    create_ARIMAParams("GBP", models.loc[models['MAPE_GBP'].idxmin()].P,
                        models.loc[models['MAPE_GBP'].idxmin()].D, models.loc[models['MAPE_GBP'].idxmin()].Q)
    create_ARIMAParams("EUR", models.loc[models['MAPE_EUR'].idxmin()].P,
                        models.loc[models['MAPE_EUR'].idxmin()].D, models.loc[models['MAPE_EUR'].idxmin()].Q)
