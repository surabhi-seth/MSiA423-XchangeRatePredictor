'''from app import db
from app.models import Track
import argparse
import logging.config
logger = logging.getLogger(__name__)


def create_db(args):
    """Creates a database with the data model given by obj:`apps.models.Track`

    Args:
        args: Argparse args - should include args.title, args.artist, args.album

    Returns: None

    """

    db.create_all()

    track = Track(artist=args.artist, album=args.album, title=args.title)
    db.session.add(track)
    db.session.commit()
    logger.info("Database created with song added: %s by %s from album, %s ", args.title, args.artist, args.album)


def add_track(args):
    """Seeds an existing database with additional songs.

    Args:
        args: Argparse args - should include args.title, args.artist, args.album

    Returns:None

    """

    track = Track(artist=args.artist, album=args.album, title=args.title)
    db.session.add(track)
    db.session.commit()
    logger.info("%s by %s from album, %s, added to database", args.title, args.artist, args.album)


if __name__ == '__main__':

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers()

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create", description="Create database")
    sb_create.add_argument("--artist", default="Britney Spears", help="Artist of song to be added")
    sb_create.add_argument("--title", default="Radar", help="Title of song to be added")
    sb_create.add_argument("--album", default="Circus", help="Album of song being added.")
    sb_create.set_defaults(func=create_db)

    # Sub-parser for ingesting new data
    sb_ingest = subparsers.add_parser("ingest", description="Add data to database")
    sb_ingest.add_argument("--artist", default="Emancipator", help="Artist of song to be added")
    sb_ingest.add_argument("--title", default="Minor Cause", help="Title of song to be added")
    sb_ingest.add_argument("--album", default="Dusk to Dawn", help="Album of song being added")
    sb_ingest.set_defaults(func=add_track)

    args = parser.parse_args()
    args.func(args)
'''

from app import db
from app.models import Rates, ARIMAParams
from . import START_DATE, END_DATE
#import argparse

import requests
import pandas as pd

import logging.config
logger = logging.getLogger(__name__)


def create_db():
    """Creates a database with rates from the api
    Returns: None
    """
    url = "https://api.exchangeratesapi.io/history?start_at=" + START_DATE + "&end_at=" + END_DATE + "&base=USD"
    response = requests.get(url)
    result = response.json()

    dates_list = list(result['rates'].keys())
    inputs = {
        'DATE': [date for date in dates_list],
        'EUR': [result['rates'][date]['EUR'] for date in dates_list],
        'INR': [result['rates'][date]['INR'] for date in dates_list],
        'GBP': [result['rates'][date]['GBP'] for date in dates_list]
    }

    rates = pd.DataFrame(data=inputs)
    rates = rates.sort_values(by=['DATE'], ascending=True).reset_index(drop=True)

    db.drop_all()
    db.create_all()
    db.session.bulk_insert_mappings(Rates, rates.to_dict(orient="records"))
    db.session.commit()
    logger.info("Database created with rates")


def create_ARIMAParams(currency, p, d, q):
    ARIMAParams.query.filter_by(CURRENCY=currency).delete()
    params = ARIMAParams(CURRENCY=currency, P=p, D=d, Q=q)
    db.session.add(params)
    db.session.commit()
