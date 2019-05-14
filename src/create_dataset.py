import config
import logging.config
import yaml
import sys

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker

from src.helpers.helpers import create_connection, get_session


logger = logging.getLogger(__name__)
logger.setLevel("INFO")

Base = declarative_base()

class ARIMA_Params(Base):
    """Create a data model for the database to be set up for capturing songs
    """

    __tablename__ = 'ARIMA_Params'

    CURRENCY = Column(String(10), primary_key=True)
    P = Column(Integer, unique=False, nullable=False)
    D = Column(Integer, unique=False, nullable=False)
    Q = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        return '<ARIMA Params %r>' % self.CURRENCY


def create_db():
    """Creates a database with ARIMA_Params table
    Returns: None
    """
    dbconfig = config.DBCONFIG
    try:
        if dbconfig is not None:
            engine = create_connection(dbconfig=config.DBCONFIG)
            logger.info("Creating RDS database")
        else:
            engine = create_connection(engine_string=config.SQLALCHEMY_DATABASE_URI)
            logger.info("Creating sqlite database")

        #Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        logger.info("Database created with tables")
    except Exception as e:
        logger.error(e)
        sys.exit(1)

def create_ARIMA_Params(currency, p, d, q):
    dbconfig = config.DBCONFIG
    try:
        if dbconfig is not None:
            session = get_session(dbconfig=dbconfig)
        else:
            session = get_session(engine_string=config.SQLALCHEMY_DATABASE_URI)

        ARIMA_Params.query.filter_by(CURRENCY=currency).delete()
        params = ARIMA_Params(CURRENCY=currency, P=p, D=d, Q=q)
        session.add(params)
        session.commit()
        logger.info("ARIMA Model parameters loaded in the db")
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    finally:
        session.close()
