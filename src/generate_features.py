import logging
import argparse
import yaml
import os
import subprocess
import re
import boto3
import sqlalchemy
import pandas as pd

from src.load_data import load_data, load_column_as_list
from src.helpers.helpers import fillin_kwargs

logger = logging.getLogger(__name__)


def choose_features(df, features_to_use=None, target=None, save_path=None, **kwargs):
    """Reduces the dataset to the features_to_use. Will keep the target if provided.

    Args:
        df (:py:class:`pandas.DataFrame`): DataFrame containing the features
        features_to_use (:obj:`list`): List of columnms to extract from the dataset to be features
        target (str, optional): If given, will include the target column in the output dataset as well.
        save_path (str, optional): If given, will save the feature set (and target, if applicable) to the given path.
        **kwargs:

    Returns:
        X (:py:class:`pandas.DataFrame`): DataFrame containing extracted features (and target, it applicable)
    """

    logger.debug("Choosing features")
    if features_to_use is not None:
        features = []
        dropped_columns = []
        for column in df.columns:
            # Identifies if this column is in the features to use or if it is a dummy of one of the features to use
            if column in features_to_use or column.split("_dummy_")[0] in features_to_use or column == target:
                features.append(column)
            else:
                dropped_columns.append(column)

        if len(dropped_columns) > 0:
            logger.info("The following columns were not used as features: %s", ",".join(dropped_columns))
        logger.debug(features)
        X = df[features]
    else:
        logger.debug("features_to_use is None, df being returned")
        X = df

    if save_path is not None:
        X.to_csv(save_path, **kwargs)

    return X


def get_target(df, target, save_path=None, **kwargs):

    y = df[target]

    if save_path is not None:
        y.to_csv(save_path, **kwargs)

    return y.values


def bin_values(df, columns, bins=None, quartiles=None, new_column=False, **kwargs):
    columns = [columns] if type(columns) != list else columns

    if bins is not None and quartiles is not None:
        raise ValueError("Only bins or quartiles can be done at one time.")
    elif bins is None and quartiles is None:
        raise ValueError("Specify bins or quartiles")
    else:
        for j, column in enumerate(columns):
            column_name = "%s_binned" if new_column else column
            if bins is not None:
                bins_input = bins[j] if type(bins) == list and len(bins) == len(columns) else bins
                df[column_name] = pd.cut(df[column], bins=bins_input, labels=range(bins_input))
            else:

                quartiles_input = quartiles[j] if type(quartiles) == list else quartiles
                df[column_name] = pd.qcut(df[column], q=quartiles_input, labels=range(quartiles_input))

    return df


def make_categorical(df, columns, one_hot=False, **kwargs):
    columns = [columns] if type(columns) != list else columns

    for column in columns:
        one_hot_col = False
        if column in kwargs:
            if "load_column_as_list" in kwargs[column]:
                categories = load_column_as_list(**kwargs[column]["load_column_as_list"])
                logger.info("Categories loaded as %s", ",".join(categories))
            elif "categories" in kwargs[column]:
                categories = kwargs[column]["categories"]
            else:
                categories = df[column].unique()

            if "one_hot_encode" in kwargs[column] and kwargs[column]["one_hot_encode"]:
                one_hot_col = True

        df[column] = pd.Categorical(df[column], categories=categories)

        if one_hot or one_hot_col:
            df = one_hot_encode(df, column)

    return df


def one_hot_encode(df, columns, drop_original=True):
    columns = [columns] if type(columns) != list else columns

    for column in columns:
        dummies = pd.get_dummies(df[column])
        dummies.columns = ["%s_dummy_%i" % (column, j) for j in range(len(dummies.columns))]
        df = pd.concat([df, dummies], axis=1)

    if drop_original:
        df = df.drop(labels=columns, axis=1)

    return df


def drop_na(df, columns=None):
    if columns is not None:
        columns = [columns] if type(columns) == str else columns
        num_nas = df[columns].isna().sum()
        for col in columns:
            logger.info("There were %i missing %s values", num_nas.loc[col], col)
        df_len = len(df)
        df = df.dropna(subset=columns)
        logger.warning("%i values were dropped from the dataset because of missing values", df_len - len(df))
    else:
        logger.warning("No columns provided for dropna")

    return df


def generate_features(df, save_features=None, **kwargs):
    """

    Args:
        df (:py:class:`pandas.DataFrame`): DataFrame containing the data to be transformed into features.
        save_features (str, optional): If given, the feature set will be saved to this path.
        **kwargs: Should contain the arguments for each transformation to be performed on the data, `df`.
            This function assumes each kwarg given except "choose_features" and "get_target" are functions in this file
            that should be evaluated.

    Returns:

    """

    # Evaluates each function corresponding to a key in `kwargs` and using the key's values as parameters
    # for that function. The functions "choose_features" and "get_target" are not evaluated until after
    # this step.
    for step in kwargs:
        if step not in ["choose_features", "get_target"]:
            command = "%s(df, **kwargs[step])" % step
            logging.debug("Generating feature via %s", command)
            df = eval(command)

    choose_features_kwargs = fillin_kwargs("choose_features", kwargs)["choose_features"]
    df = choose_features(df, **choose_features_kwargs)

    if save_features is not None:
        df.to_csv(save_features)

    return df


def run_features(args):
    """Orchestrates the generating of features from commandline arguments."""
    with open(args.config, "r") as f:
        config = yaml.load(f)

    if args.input is not None:
        df = pd.read_csv(args.input)
    elif "load_data" in config:
        df = load_data(config["load_data"])
    else:
        raise ValueError("Path to CSV for input data must be provided through --csv or "
                         "'load_data' configuration must exist in config file")

    df = generate_features(df, **config["generate_features"])

    if args.output is not None:
        df.to_csv(args.output)
        logger.info("Features saved to %s", args.output)

    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate features")
    parser.add_argument('--config', help='path to yaml file with configurations')
    parser.add_argumemt('--input', default=None, help="Path to CSV for generating features from")

    args = parser.parse_args()

    run_features(args)
