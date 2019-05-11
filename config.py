from os import path

# Getting the parent directory of this file. That will function as the project home.
PROJECT_HOME = path.dirname(path.abspath(__file__))
DBCONFIG = path.join(PROJECT_HOME, 'config/dbconfig.yml')
MODEL_CONFIG = path.join(PROJECT_HOME, 'config/model_config.yml')

DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 3000
APP_NAME = "penny-lane"
SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/surabhis/PycharmProjects/rates.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "127.0.0.1"
