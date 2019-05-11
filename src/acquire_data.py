import json
import requests
import boto3
import yaml
import config
from os import path

import logging.config
logger = logging.getLogger(__name__)


def acquire_rates():
    """Calls API to get exchange rate data
    Returns: JSON response
    """
    with open(config.MODEL_CONFIG, "r") as f:
        model_config = yaml.load(f)

    load_config = model_config["acquire_rates"]
    base_url = load_config["BASE_URL"]
    start_date = load_config["START_DATE"]
    end_date = load_config["END_DATE"]
    api_url = "{base_url}?start_at={start_date}&end_at={end_date}&base=USD"
    api_url = api_url.format(base_url=base_url, start_date=start_date,
                                         end_date=end_date)
    logger.info(api_url)
    response = requests.get(api_url)
    result = response.json()

    file_location = path.join(config.PROJECT_HOME, load_config["RAW_DATA_LOCATION"])
    logger.info(file_location)
    write_records(result, file_location)

    bucket_name = load_config["S3_LOCATION"]
    file_name = load_config["S3_FILE_NAME"]
    write_to_S3(file_location, bucket_name, file_name)


def write_records(records, file_location):
    """Persist API response set to file.

    Args:
        records (`:obj:`list` of :obj:`str`): JSON containing exchange rate data.
        file_location (`str`): Location to write file to.

    Returns:
        None
    """

    if not file_location:
        raise FileNotFoundError

    num_records = len(records)
    logger.debug("Writing {} records to {}".format(num_records, file_location))

    with open(file_location, "w+") as output_file:
        json.dump(records, output_file, indent=2)


def write_to_S3(file_location, bucket_name, file_name):
    # Boto 3
    s3 = boto3.resource('s3')
    s3.Object(bucket_name, file_name).put(Body=open(file_location, 'rb'))
    return