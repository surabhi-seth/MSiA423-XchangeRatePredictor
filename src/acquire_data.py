import sys
import json
import requests
import boto3
import yaml
import config
import botocore
from os import path
from src.helpers.helpers import invoke_api

import logging.config
logger = logging.getLogger(__name__)


def acquire_rates(args):
    """Calls API to get exchange rate data and dumps the JSON in S3 bucket
    """
    try:
        with open(config.MODEL_CONFIG, "r") as f:
            model_config = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    # Construct the API URL from the configs set in the yaml
    load_config = model_config["acquire_rates"]
    base_url = load_config["BASE_URL"]
    start_date = load_config["START_DATE"]
    end_date = load_config["END_DATE"]
    api_url = "{base_url}?start_at={start_date}&end_at={end_date}&base=USD"
    api_url = api_url.format(base_url=base_url, start_date=start_date,
                                         end_date=end_date)
    logger.debug(api_url)

    result = invoke_api(api_url)

    # Store the JSON locally first
    file_location = path.join(config.PROJECT_HOME, load_config["RAW_DATA_LOCATION"])
    logger.debug(file_location)
    write_records(result, file_location)

    # Now dump it to S3 bucket
    bucket_name = load_config["S3_LOCATION"]
    file_name = load_config["S3_FILE_NAME"]
    write_to_S3(file_location, bucket_name, file_name)


def write_records(records, file_location):
    """Persist API response set to file.

    Args:
        records: JSON containing exchange rate data.
        file_location: Location to write file to.

    Returns:
        None
    """
    try:
        if not file_location:
            raise FileNotFoundError

        num_records = len(records)
        logger.debug("Writing {} records to {}".format(num_records, file_location))

        with open(file_location, "w+") as output_file:
            json.dump(records, output_file, indent=2)

    except FileNotFoundError:
        logger.error("Please provide a valid file location to persist data.")
        sys.exit(1)


def write_to_S3(file_location, bucket_name, file_name):
    """
    :param file_location: The local file location from where the JSON will be retrieved
    :param bucket_name: The S3 bucket where the retrieved JSON will be stored
    :param file_name: The file name within the S3 bucket in which the retrieved JSON will be stored
    :return: None
    """
    try:
        s3 = boto3.resource('s3')
        s3.Object(bucket_name, file_name).put(Body=open(file_location, 'rb'))
        logger.info("JSON uploaded to S3 bucket")
    except botocore.exceptions.NoCredentialsError as e:
        logger.error("Invalid S3 credentials")
        sys.exit(1)