import json
import requests
import config
import boto3
from boto.s3.key import Key

from . import START_DATE, END_DATE
import logging.config
logger = logging.getLogger(__name__)


def acquire_rates():
    """Calls API to get exchange rate data
    Returns: JSON response
    """
    url = "https://api.exchangeratesapi.io/history?start_at=" + START_DATE + "&end_at=" + END_DATE + "&base=USD"
    response = requests.get(url)
    result = response.json()
    logger.info(config.PROJECT_HOME)
    write_records(result, config.RAW_DATA_LOCATION)


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

    write_to_S3(file_location)


def write_to_S3(file_location):
    # Boto 3
    s3 = boto3.resource('s3')
    s3.Object('nw_surabhiseth-s3', 'raw_exchange_rates.txt').put(Body=open(file_location, 'rb'))
    return