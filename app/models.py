import logging
from app import db

logger = logging.getLogger(__name__)

db.Model.metadata.reflect(db.engine)

'''
class Rates(db.Model):
    """Create a data model for the database to be set up for capturing rates
    """
    DATE = db.Column(db.TEXT, primary_key=True)
    EUR = db.Column(db.REAL, unique=False)
    INR = db.Column(db.REAL, unique=False)
    GBP = db.Column(db.REAL, unique=False)

    def __repr__(self):
        return '<Rates %r>' % self.DATE
'''

class ARIMA_Params(db.Model):
    """Create a data model for the database to be set up for capturing ARIMA parameters
    """
    CURRENCY = db.Column(db.TEXT, primary_key=True)
    P = db.Column(db.INTEGER, unique=False)
    D = db.Column(db.INTEGER, unique=False)
    Q = db.Column(db.INTEGER, unique=False)

    def __repr__(self):
        return '<ARIMA Params %r>' % self.CURRENCY