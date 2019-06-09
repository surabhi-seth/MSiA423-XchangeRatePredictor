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
logger = logging.getLogger("run-xchangeratepred")

from src.create_dataset import create_db
from src.acquire_data import acquire_rates
from src.train_model import train_model
from src.score_model import score_model
from app.app import app

def run_app(args):
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run components of the model source code")
    subparsers = parser.add_subparsers()

    # Sub-parser for acquiring exchange rate data
    sb_acquire = subparsers.add_parser("acquire", description="Acquire exchange rate data")
    sb_acquire.set_defaults(func=acquire_rates)

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create rates database")
    sb_create.set_defaults(func=create_db)

    # Sub-parser for training the model
    sb_train = subparsers.add_parser("train", description="Train ARIMA models")
    sb_train.set_defaults(func=train_model)

    # Sub-parser for scoring the model
    sb_score = subparsers.add_parser("score", description="Score Predictions")
    sb_score.set_defaults(func=score_model)

    # Sub-parser for running flask app
    sb_run = subparsers.add_parser("app", description="Run Flask app")
    sb_run.set_defaults(func=run_app)

    args = parser.parse_args()
    args.func(args)
