import logging
import argparse
import yaml
import os
import subprocess
import re
import datetime

import pickle

import sklearn
import xgboost
import pandas as pd
import numpy as np

from src.load_data import load_data
from src.helpers import Timer, fillin_kwargs
from src.generate_features import choose_features, get_target
from sklearn.linear_model import LogisticRegression, LinearRegression

logger = logging.getLogger(__name__)

score_model_kwargs = ["predict"]


def score_model(df, path_to_tmo, save_scores=None, **kwargs):

    with open(path_to_tmo, "rb") as f:
        model = pickle.load(f)

    kwargs = fillin_kwargs(score_model_kwargs, kwargs)

    if "choose_features" in kwargs:
        X = choose_features(df, **kwargs["choose_features"])
    else:
        X = df

    with Timer("scoring", logger):
        y_predicted = model.predict(X, **kwargs["predict"])

    if save_scores is not None:
        pd.DataFrame(y_predicted).to_csv(save_scores,  index=False)

    return y_predicted


def run_scoring(args):
    with open(args.config, "r") as f:
        config = yaml.load(f)

    if args.input is not None:
        df = pd.read_csv(args.input)
    elif "generate_features" in config and "save_features" in config["generate_features"]:
        df = pd.read_csv(config["generate_features"]["save_features"])
    else:
        raise ValueError("Path to CSV for input data must be provided through --input or "
                         "'load_data' configuration must exist in config file")

    y_predicted = score_model(df, **config["score_model"])

    if args.output is not None:
        pd.DataFrame(y_predicted).to_csv(args.output, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Score model")
    parser.add_argument('--config', '-c', help='path to yaml file with configurations')
    parser.add_argumemt('--input', '-i', default=None, help="Path to CSV for input to model scoring")
    parser.add_argument('--output', '-o', default=None, help='Path to where the scores should be saved to (optional)')

    args = parser.parse_args()

    run_scoring(args)

