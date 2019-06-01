import pandas as pd
import sys
import json
import yaml
import config
import boto3
from os import path
from src.helpers.helpers import get_engine

import logging.config
logger = logging.getLogger(__name__)


def load_ARIMA_Params(engine):
    """ Load p,d,q parameters corresponding to the best ARIMA models from the database """

    try:
        query = "SELECT * FROM ARIMA_Params"
        ARIMA_Params = pd.read_sql(query, con=engine)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    return ARIMA_Params;


def read_records(file_location):
    """ Read and load JSON from the local filesystem """
    try:
        if not file_location:
            raise FileNotFoundError

        with open(file_location, 'r+') as input_file:
            try:
                output_records = json.load(input_file)
            except json.decoder.JSONDecodeError:
                logger.error("Could not decode JSON")
    except FileNotFoundError:
        logger.error("Source data file not found")
        sys.exit(1)

    return output_records


def load_raw_source(local_results_file):
    """ Fetch the source data stored in S3 bucket """
    try:
        with open(config.MODEL_CONFIG, "r") as f:
            model_config = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    # Get raw data from S3 bucket
    load_config = model_config["acquire_rates"]
    bucket_name = load_config["S3_LOCATION"]
    file_name = load_config["S3_FILE_NAME"]

    s3 = boto3.resource("s3")
    s3.meta.client.download_file(bucket_name, file_name, local_results_file)
    return

