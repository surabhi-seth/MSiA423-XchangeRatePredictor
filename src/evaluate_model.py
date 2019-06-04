from statsmodels.tsa.arima_model import ARIMA
import pandas as pd

'''
ARIMA_models = {
        'P': [1, 0, 0, 2, 0],
        'D': [1, 1, 1, 1, 1],
        'Q': [0, 0, 1, 0, 2]
    }

0, 0, 1
0, 1, 0
1, 0, 0
0, 1, 1
1, 0, 1
1, 1, 0
1, 1, 1

2, 0, 0
0, 2, 0
0, 0, 2

2, 1, 0
2, 0, 1
0, 2, 1

1, 0, 2'''

def ARIMAForecasting(ts, FORECAST_PERIOD, P, D, Q):
    """ Runs ARIMA for the p,d,q parameters on the time series and generates predictions for the forecast period """
    print(P, D, Q)
    model = ARIMA(ts, order=(P, D, Q))
    model_fit = model.fit(disp=0, maxiter=2000, method='css')
    prediction = model_fit.forecast(steps=FORECAST_PERIOD)[0]
    return prediction


def evaluate_model(rates, FORECAST_PERIOD, ARIMA_models, **kwargs):
    """
    Evaluates different ARIMA models and returns corresponding MAPE values
    :param rates: Exchange rate data
    :param FORECAST_PERIOD: Number of days for which predictions are to be generated
    :param kwargs: yaml config
    :return: Different ARIMA models with corresponding MAPE values from training
    """
    models = pd.DataFrame(data=ARIMA_models)
    MAPE_INR = []
    MAPE_EUR = []
    MAPE_GBP = []

    for i in range(len(ARIMA_models['P'])):
        # INR GBP training and predictions
        predictions_INR = ARIMAForecasting(rates.INR[0:len(rates.INR) - FORECAST_PERIOD], FORECAST_PERIOD,
                                           ARIMA_models['P'][i], ARIMA_models['D'][i], ARIMA_models['Q'][i])
        MAPE_INR.append(sum(abs(predictions_INR - rates.INR[len(rates.INR) - FORECAST_PERIOD:len(rates.INR)])) / \
                            sum(rates.INR[len(rates.INR) - FORECAST_PERIOD:len(rates.INR)]))

        # EUR GBP training and predictions
        predictions_EUR = ARIMAForecasting(rates.EUR[0:len(rates.EUR) - FORECAST_PERIOD], FORECAST_PERIOD,
                                           ARIMA_models['P'][i], ARIMA_models['D'][i], ARIMA_models['Q'][i])
        MAPE_EUR.append(sum(abs(predictions_EUR - rates.EUR[len(rates.EUR) - FORECAST_PERIOD:len(rates.EUR)])) / \
                        sum(rates.EUR[len(rates.EUR) - FORECAST_PERIOD:len(rates.EUR)]))

        # GBP training and predictions
        predictions_GBP = ARIMAForecasting(rates.GBP[0:len(rates.GBP) - FORECAST_PERIOD], FORECAST_PERIOD,
                                           ARIMA_models['P'][i], ARIMA_models['D'][i], ARIMA_models['Q'][i])
        MAPE_GBP.append(sum(abs(predictions_GBP - rates.GBP[len(rates.GBP) - FORECAST_PERIOD:len(rates.GBP)])) / \
                        sum(rates.GBP[len(rates.GBP) - FORECAST_PERIOD:len(rates.GBP)]))

    #Append the MAPE values to the different models
    models['MAPE_INR'] = MAPE_INR
    models['MAPE_EUR'] = MAPE_EUR
    models['MAPE_GBP'] = MAPE_GBP
    return(models)


