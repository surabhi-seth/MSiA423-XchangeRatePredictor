from app import db
import pandas as pd
import sys
import json
import requests
import boto3
import yaml
import config
import boto3
from os import path

import logging.config
logger = logging.getLogger(__name__)


'''def load_Rates():
    rates = pd.read_sql_query("select * from Rates", con=db.engine);
    return rates;


def get_latest_rates():
    latest_rates = pd.read_sql_query("select * from Rates order by DATE desc limit 1", con=db.engine);
    return latest_rates;'''


def load_ARIMAParams():
    ARIMAParams = pd.read_sql_query("select * from ARIMA_Params", con=db.engine);
    return ARIMAParams;

def load_raw_source(local_results_file):
    try:
        with open(config.MODEL_CONFIG, "r") as f:
            model_config = yaml.load(f)
    except FileNotFoundError:
        logger.error("YAML not found")
        sys.exit(1)

    load_config = model_config["acquire_rates"]

    # Get raw data from S3 bucket
    bucket_name = load_config["S3_LOCATION"]
    file_name = load_config["S3_FILE_NAME"]

    s3 = boto3.resource("s3")
    s3.meta.client.download_file(bucket_name, file_name, local_results_file)

    return
