import os
from os import path

conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
DATABASE_NAME = 'msia423'
#SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".\
#    format(conn_type, user, password, host, port, DATABASE_NAME)

# Use the following SQLALCHEMY_DATABASE_URI for sqlite
PROJECT_HOME = path.dirname(path.abspath(__file__))
DB_PATH = path.join(PROJECT_HOME, 'data/XchangeRatePredictor.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)

SQLALCHEMY_TRACK_MODIFICATIONS = True

# Flask config
HOST = "0.0.0.0" #"18.188.190.59"
PORT = 3000
APP_NAME = "xchangeratepred"

DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"