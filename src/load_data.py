from app import db
import pandas as pd
import sys
import json
import boto3
import yaml
import config
import boto3
from os import path
from src.helpers.helpers import get_session, get_engine
from src.create_dataset import ARIMA_Params

import logging.config
logger = logging.getLogger(__name__)


def load_ARIMA_Params(args):
    engine = get_engine(args)

    try:
        session = get_session(engine)
        model_params = session.query(ARIMA_Params.CURRENCY, ARIMA_Params.P, ARIMA_Params.D, ARIMA_Params.Q)
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    finally:
        session.close()

    #ARIMAParams = pd.read_sql_query("select * from ARIMA_Params", con=db.engine);
    return model_params;

def load_raw_source(local_results_file):
    try:
        with open(config.MODEL_CONFIG, "r") as f:
            model_config = yaml.load(f)
    except FileNotFoundError:
        logger.error("YAML not found")
        sys.exit(1)

    # Get raw data from S3 bucket
    load_config = model_config["acquire_rates"]
    bucket_name = load_config["S3_LOCATION"]
    file_name = load_config["S3_FILE_NAME"]

    s3 = boto3.resource("s3")
    s3.meta.client.download_file(bucket_name, file_name, local_results_file)
    return

