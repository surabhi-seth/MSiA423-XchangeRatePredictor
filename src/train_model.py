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



def find_best_model(models):
    """
    Determine the best model from the MAPE values for INR, GBP and EUR
    :param models: Dataframe containing ARIMA model parameters with corresponding MAPE values
    :return: Dataframe with the best INR, GBP and EUR models
    """

    best_models = pd.DataFrame(columns=['CURRENCY', 'P', 'D', 'Q'])

    # Find the best model for INR, GBP and EUR
    best_INR_model = models.loc[models['MAPE_INR'].idxmin()]
    best_models = best_models.\
        append({'CURRENCY': 'INR', 'P': best_INR_model.P, 'D': best_INR_model.D, 'Q': best_INR_model.Q,
                'MAPE': best_INR_model.MAPE_INR}, ignore_index=True)

    best_GBP_model = models.loc[models['MAPE_GBP'].idxmin()]
    best_models = best_models. \
        append({'CURRENCY': 'GBP', 'P': best_GBP_model.P, 'D': best_GBP_model.D, 'Q': best_GBP_model.Q,
                'MAPE': best_GBP_model.MAPE_GBP}, ignore_index=True)

    best_EUR_model = models.loc[models['MAPE_EUR'].idxmin()]
    best_models = best_models. \
        append({'CURRENCY': 'EUR', 'P': best_EUR_model.P, 'D': best_EUR_model.D, 'Q': best_EUR_model.Q,
               'MAPE': best_EUR_model.MAPE_EUR}, ignore_index=True)

    best_models = best_models.sort_values(by=['CURRENCY'], ascending=True).reset_index(drop=True)

    return best_models


def store_best_models(df):
    """
    Stores the ARIMA parameters passed in the input df in the database
    :param df: ARIMA parameters corresponding to the best models
    :return: None
    """
    engine = get_engine()
    create_ARIMA_Params(engine, df)
    logger.info("ARIMA Model parameters loaded in the db")


def train_model(args):
    """
    Orchestrates the following steps:
    1. Fetch the source data from S3 bucket
    2. Evaluate the MAPE values for various ARIMA models for INR, GBP and EUR
    3. Find the best models with the lowest MAPE value for INR, GBP and EUR respectively
    4. Insert the p,d,q values for the best ARIMA models
    """

    try:
        with open(config.MODEL_CONFIG, "r") as f:
            model_config = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    # 1. Fetch the source data from S3 bucket
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

    # 2. Evaluate the MAPE values for various ARIMA models for INR, GBP and EUR
    models = evaluate_model(rates, **load_config)

    # 3. Find the best models with the lowest MAPE value for INR, GBP and EUR respectively
    best_models = find_best_model(models)

    # 4. Insert the p,d,q values for the best ARIMA models
    store_best_models(best_models)

    return