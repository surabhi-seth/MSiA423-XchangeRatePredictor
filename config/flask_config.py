import os

conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
DATABASE_NAME = 'msia423'
SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".\
    format(conn_type, user, password, host, port, DATABASE_NAME)
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Flask config
HOST = "0.0.0.0" #"18.188.190.59"
PORT = 3000
APP_NAME = "xchangeratepred"

DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"