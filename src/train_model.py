from statsmodels.tsa.arima_model import ARIMA
from . import FORECAST_PERIOD


def ARIMAForecasting(Actual, P, D, Q):
    model = ARIMA(Actual, order=(P, D, Q))
    model_fit = model.fit(disp=0)
    prediction = model_fit.forecast(steps=FORECAST_PERIOD)[0]
    return prediction
