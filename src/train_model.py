import sys
import json
import requests
import boto3
import yaml
import config
import pandas as pd
from os import path
from src.load_data import load_raw_source, read_records
from src.create_dataset import create_ARIMA_Params
from src.evaluate_model import evaluate_model
from src.helpers.helpers import get_engine

import logging.config
logger = logging.getLogger(__name__)



def store_best_model(args, models):
    """ Determine the best model from the MAPE values and store its parameters in the databse a"""

    # Find the best model for INR, GBP and EUR
    best_INR_model = models.loc[models['MAPE_INR'].idxmin()]
    best_GBP_model = models.loc[models['MAPE_GBP'].idxmin()]
    best_EUR_model = models.loc[models['MAPE_EUR'].idxmin()]

    # Insert the p,d,q values for the best ARIMA model
    engine = get_engine()
    create_ARIMA_Params(engine, "INR", best_INR_model.P, best_INR_model.D, best_INR_model.Q)
    create_ARIMA_Params(engine, "GBP", best_GBP_model.P, best_GBP_model.D, best_GBP_model.Q)
    create_ARIMA_Params(engine, "EUR", best_EUR_model.P, best_EUR_model.D, best_EUR_model.Q)
    logger.info("ARIMA Model parameters loaded in the db")

    return

def train_model(args):
    """
    Orchestrates the following steps:
    1. Fetch the source data from S3 bucket
    2. Evaluate the best ARIMA model for INR, GBP and EUR
    3. Store the model params for the best model
    """

    try:
        with open(config.MODEL_CONFIG, "r") as f:
            model_config = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logger.error("YAML not found")
        sys.exit(1)

    load_config = model_config["train_model"]
    local_results_file = load_config["DOWNLOAD_LOCATION"]
    load_raw_source(local_results_file)
    data = read_records(local_results_file)

    dates_list = list(data['rates'].keys())
    inputs = {
            'DATE': [date for date in dates_list],
            'EUR': [data['rates'][date]['EUR'] for date in dates_list],
            'INR': [data['rates'][date]['INR'] for date in dates_list],
            'GBP': [data['rates'][date]['GBP'] for date in dates_list]
            }

    rates = pd.DataFrame(data=inputs)
    rates = rates.sort_values(by=['DATE'], ascending=True).reset_index(drop=True)

    models = evaluate_model(rates, **load_config)
    store_best_model(args, models)
    return