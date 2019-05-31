import os
import datetime
import sqlalchemy
import yaml
import sys
import requests
from sqlalchemy.orm import sessionmaker
import config
import logging

logger = logging.getLogger(__name__)


class Timer:
    """Times the code within the with statement and logs the elapsed time when it closes.
           Args:
               function_name(string): Name of function being timed
               logger (obj:`logging.logger`): Logger to have elapsed time logged to
   """
    def __init__(self, function_name, logger):
        self.logger = logger
        self.function = function_name

    def __enter__(self):
        self.start = datetime.datetime.now()

        return self

    def __exit__(self, *args):
        self.end = datetime.datetime.now()
        self.interval = self.end - self.start
        self.logger.info("%s took %0.2f seconds", self.function, self.interval.total_seconds())


def format_sql(sql, replace_sqlvar=None, replace_var=None, python=True):
    """Formats SQL query string for Python interpretation and with variables replaced.
    Args:
        sql (string): String with SQL query
        replace_sqlvar (dict, optional): If given, replaces variables of the format ${var:dict-key} with the value
            in the dictionary corresponding to that dict-key.
        replace_var (dict, optional): If given, replaces variables of the format {dict-key} with the value
            in the dictionary corresponding to that dict-key.
        python: If True, formats the query to be passed into a Python SQL querying function by replacing "%" with
            "%%" since % is a special character in Python
    Returns: string of SQL query with variables replaced and optionally formatted for Python
    """
    if replace_sqlvar is not None:
        for var in replace_sqlvar:
            sql = sql.replace("${var:%s}" % var, replace_sqlvar[var])

    if replace_var is not None:
        sql = sql.format(**replace_var)

    if python:
        sql = sql.replace("%", "%%")

    return sql


def load_sql(path_to_sql, load_comments=False, replace_sqlvar=None, replace_var=None, python=True):
    sql = ""
    with open(path_to_sql, "r") as f:
        for line in f.readlines():
            if not load_comments and not line.startswith("--"):
                sql += line

    sql = format_sql(replace_sqlvar=replace_sqlvar, replace_var=replace_var, python=python)

    return sql


def ifin(param, dictionary, alt=None):

    assert type(dictionary) == dict
    if param in dictionary:
        return dictionary[param]
    else:
        return alt


def create_connection(host='127.0.0.1', database="", sqltype="mysql+pymysql", port=3308,
                      user_env="amazonRDS_user", password_env="amazonRDS_pw",
                      username=None, password=None, dbconfig=None, engine_string=None):

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


def get_engine(args):
    '''Creates engine for an RDS or local sqlite database'''
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


def invoke_api(api_url):
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

def fillin_kwargs(keywords, kwargs):
    keywords = [keywords] if type(keywords) != list else keywords

    logger.debug("Original keywords in kwargs: %s", ",".join(kwargs.keys()))
    for keyword in keywords:
        if keyword not in kwargs:
            kwargs[keyword] = {}
    return kwargs