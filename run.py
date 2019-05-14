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
    sb_create.set_defaults(func=create_db)

    args = parser.parse_args()
    args.func()

'''# Sub-parser for scoring the final model
    sb_increment = subparsers.add_parser("increment", description="Increment Rates Data")
    sb_increment.set_defaults(func=increment_rate_data)

    # Sub-parser for evaluating models
    sb_evaluate = subparsers.add_parser("evaluate", description="Evaluate ARIMA Models")
    sb_evaluate.set_defaults(func=evaluate_model)

    # Sub-parser for scoring the final model
    sb_score = subparsers.add_parser("score", description="Score ARIMA Models")
    sb_score.set_defaults(func=score_model)'''

