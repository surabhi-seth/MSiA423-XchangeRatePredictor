import config
import logging.config
import yaml
import sys

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, MetaData
from sqlalchemy.orm import sessionmaker

from src.helpers.helpers import create_connection, get_session, get_engine

logger = logging.getLogger(__name__)

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
    MAPE = Column(Float, unique=False, nullable=False)

    def __repr__(self):
        return '<ARIMA Params %r>' % self.CURRENCY


class Predictions(Base):
    """
        Create data model for the database for capturing predictions
        """

    __tablename__ = 'Predictions'

    CURRENCY = Column(String(10), primary_key=True)
    PRED_DATE = Column(String(20), primary_key=True)
    PRED_RATE = Column(Float, unique=False, nullable=False)

    def __repr__(self):
        return '<Predictions %r, %r>' % self.CURRENCY, self.PRED_DATE


def create_db(args):
    """Creates a RDS or a SQLITE database (based on configuration) with ARIMA_Params table
    Returns: None
    """
    engine = get_engine()
    try:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        logger.info("Database created with tables")
    except Exception as e:
        logger.error(e)
        sys.exit(1)


def create_ARIMA_Params(engine, df):
    """
    Stores ARIMA_Params in the database
    :param engine: DB engine
    :param df: Dataframe containing ARIMA parameters
    :return: None
    """

    try:
        session = get_session(engine)
        old_ARIMA_Params = session.query(ARIMA_Params.CURRENCY, ARIMA_Params.P, ARIMA_Params.D, ARIMA_Params.Q)
        old_ARIMA_Params.delete()

        session.bulk_insert_mappings(ARIMA_Params, df.to_dict(orient="records"))
        session.commit()
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    finally:
        session.close()
        return


def create_Predictions(engine, df):
    """
    Stores Predictions in the database
    :param engine: DB engine
    :param df: Dataframe containing ARIMA parameters
    :return: None
    """

    try:
        session = get_session(engine)
        old_Predictions = session.query(Predictions.CURRENCY, Predictions.PRED_DATE, Predictions.PRED_RATE)
        old_Predictions.delete()

        session.bulk_insert_mappings(Predictions, df.to_dict(orient="records"))
        session.commit()
        logger.info("Predictions stored in the database")
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    finally:
        session.close()
        return