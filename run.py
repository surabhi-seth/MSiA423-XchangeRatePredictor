"""Enables the command line execution of multiple modules within src/

This module combines the argparsing of each module within src/ and enables the execution of the corresponding scripts
so that all module imports can be absolute with respect to the main project directory.

Current commands enabled:

To create a database for Exchange Rates:

    `python run.py create_db`

To acquire the exchange rate data:

    `python run.py acquire`
"""

import argparse
import logging.config

logging.config.fileConfig("config/logging/local.conf")
logger = logging.getLogger("run-penny-lane")

from src.create_dataset import create_db
from src.acquire_data import acquire_rates
from src.train_model import train_model
from src.score_model import score_model
#from src.evaluate_model import evaluate_model
#from src.score_model import score_model
#from src.postprocess import increment_rate_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run components of the model source code")
    subparsers = parser.add_subparsers()

    # Sub-parser for acquiring exchange rate data
    sb_acquire = subparsers.add_parser("acquire", description="Acquire exchange rate data")
    sb_acquire.set_defaults(func=acquire_rates)

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create rates database")
    #sb_create.add_argument("--u", default="", help="Username for connecting to the database")
    #sb_create.add_argument("--p", default="", help="Password")
    sb_create.set_defaults(func=create_db)

    # Sub-parser for training the model
    sb_train = subparsers.add_parser("train", description="Train ARIMA models")
    #sb_train.add_argument("--u", default="", help="Username for connecting to the database")
    #sb_train.add_argument("--p", default="", help="Password")
    sb_train.set_defaults(func=train_model)

    # Sub-parser for scoring the model
    sb_score = subparsers.add_parser("score", description="Score Predictions")
    #sb_score.add_argument("--u", default="", help="Username for connecting to the database")
    #sb_score.add_argument("--p", default="", help="Password")
    sb_score.set_defaults(func=score_model)

    args = parser.parse_args()
    args.func(args)
