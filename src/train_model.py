from statsmodels.tsa.arima_model import ARIMA
import sys
import json
import requests
import boto3
import yaml
import config
from os import path
from src.load_data import load_raw_source

import logging.config
logger = logging.getLogger(__name__)

'''def ARIMAForecasting(Actual, P, D, Q):
    model = ARIMA(Actual, order=(P, D, Q))
    model_fit = model.fit(disp=0)
    prediction = model_fit.forecast(steps=FORECAST_PERIOD)[0]
    return prediction'''

def train_model(args):
    try:
        with open(config.MODEL_CONFIG, "r") as f:
            model_config = yaml.load(f)
    except FileNotFoundError:
        logger.error("YAML not found")
        sys.exit(1)

    load_config = model_config["train_model"]
    local_results_file = load_config["DOWNLOAD_LOCATION"]
    load_raw_source(local_results_file)