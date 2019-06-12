import os
import sqlalchemy
import yaml
import sys
import requests
from sqlalchemy.orm import sessionmaker
import config
import logging

logger = logging.getLogger(__name__)

def get_engine():
    '''Wrapper function for calling create_connection with the right inputs to create an engine for an RDS or sqlite database'''
    dbconfig = config.DBCONFIG
    try:
        if dbconfig is not None:
            engine = create_connection(dbconfig=config.DBCONFIG,
                                       user_env=os.environ.get("MYSQL_USER"),
                                       password_env=os.environ.get("MYSQL_PASSWORD"))
            logger.info("Accessing RDS database")
        else:
            engine = create_connection(engine_string=config.SQLALCHEMY_DATABASE_URI)
            logger.info("Accessing sqlite database")
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    return engine


def create_connection(host='127.0.0.1', database="", sqltype="mysql+pymysql", port=3308,
                      user_env="amazonRDS_user", password_env="amazonRDS_pw",
                      username=None, password=None, dbconfig=None, engine_string=None):
    """
    Creates engine for an RDS or local sqlite database
    :param host: Host
    :param database: Database name
    :param sqltype: SQltype
    :param port: Port
    :param user_env: RDS user name
    :param password_env: RDS password
    :param username: Non RDS username
    :param password: Non RDS password
    :param dbconfig: If passed, RDS connection will be created
    :param engine_string: If a sqlite connection is to be created, SQLALCHEMY_DATABASE_URI should be passed
    :return: The db connection
    """
    if engine_string is None:
        if dbconfig is not None:
            with open(dbconfig, "r") as f:
                db = yaml.load(f, Loader=yaml.FullLoader)

            host = db["host"]
            database = ifin("dbname", db, "")
            sqltype = ifin("type", db, sqltype)
            port = db["port"]
            username = user_env
            password = password_env

        username = os.environ.get(user_env) if username is None else username
        password = os.environ.get(password_env) if password is None else password

        engine_string = "{sqltype}://{username}:{password}@{host}:{port}/{database}"
        engine_string = engine_string.format(sqltype=sqltype, username=username,
                                             password=password, host=host, port=port, database=database)

    conn = sqlalchemy.create_engine(engine_string)

    return conn


def get_session(engine=None, engine_string=None):
    """
    Args:
        engine_string: SQLAlchemy connection string in the form of:
            "{sqltype}://{username}:{password}@{host}:{port}/{database}"
    Returns:
        SQLAlchemy session
    """

    if engine is None and engine_string is None:
        return ValueError("`engine` or `engine_string` must be provided")
    elif engine is None:
        engine = create_connection(engine_string=engine_string)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session


def invoke_api(api_url):
    """
    Calls the API from the url passed as input and returns the response
    :param api_url: The api url
    :return: The API response
    """
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            result = response.json()
        else:
            logger.error("API returned with status code: " + str(response.status_code))
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        logger.error("Unable to call the API")
        sys.exit(1)
    return result


def ifin(param, dictionary, alt=None):

    assert type(dictionary) == dict
    if param in dictionary:
        return dictionary[param]
    else:
        return alt