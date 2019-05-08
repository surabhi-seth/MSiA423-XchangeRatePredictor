from app import db
import pandas as pd


def load_Rates():
    rates = pd.read_sql_query("select * from Rates", con=db.engine);
    return rates;


def get_latest_rates():
    latest_rates = pd.read_sql_query("select * from Rates order by DATE desc limit 1", con=db.engine);
    return latest_rates;


def load_ARIMAParams():
    ARIMAParams = pd.read_sql_query("select * from ARIMA_Params", con=db.engine);
    return ARIMAParams;
