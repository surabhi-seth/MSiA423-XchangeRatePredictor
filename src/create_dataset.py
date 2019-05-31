import config
import logging.config
import yaml
import sys

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker

from src.helpers.helpers import create_connection, get_session, get_engine


logger = logging.getLogger(__name__)
logger.setLevel("INFO")

Base = declarative_base()

class ARIMA_Params(Base):
    """
    Create data model for the database for capturing parameters for best ARIMA models for each currency pair
    """

    __tablename__ = 'ARIMA_Params'

    CURRENCY = Column(String(10), primary_key=True)
    P = Column(Integer, unique=False, nullable=False)
    D = Column(Integer, unique=False, nullable=False)
    Q = Column(Integer, unique=False, nullable=False)

    def __repr__(self):
        return '<ARIMA Params %r>' % self.CURRENCY


def create_db(args):
    """Creates a RDS or a SQLITE database (based on configuration) with ARIMA_Params table
    Returns: None
    """
    engine = get_engine(args)
    try:
        Base.metadata.create_all(engine)
        logger.info("Database created with tables")
    except Exception as e:
        logger.error(e)
        sys.exit(1)


def create_ARIMA_Params(args, currency, p, d, q):
    """Stores ARIMA_Params in the table
        Returns: None
    """
    engine = get_engine(args)

    try:
        session = get_session(engine)
        old_ARIMA_Params = session.query(ARIMA_Params.CURRENCY, ARIMA_Params.P, ARIMA_Params.D, ARIMA_Params.Q).\
            filter_by(CURRENCY=currency)
        old_ARIMA_Params.delete()

        params = ARIMA_Params(CURRENCY=currency, P=int(p), D=int(d), Q=int(q))
        session.add(params)
        session.commit()
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    finally:
        session.close()
