from os import path

# Getting the parent directory of this file. That will function as the project home.
PROJECT_HOME = path.dirname(path.abspath(__file__))

# DBCONFIG specifies the yaml file with settings for creation of RDS database
# DBCONFIG = None
DBCONFIG = path.join(PROJECT_HOME, 'config/dbconfig.yml')
MODEL_CONFIG = path.join(PROJECT_HOME, 'config/model_config.yml')


# The SQLALCHEMY_DATABASE_URI parameter is considered ONLY if DBCONFIG is set as None. Else it is ignored.
DB_PATH = path.join(PROJECT_HOME, 'data/XchangeRatePredictor.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)
SQLALCHEMY_TRACK_MODIFICATIONS = True
