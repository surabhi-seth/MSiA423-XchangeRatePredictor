from app import db

'''
class Track(db.Model):
    """Create a data model for the database to be set up for capturing songs

    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    artist = db.Column(db.String(100), unique=False, nullable=False)
    album = db.Column(db.String(100), unique=False, nullable=True)

    def __repr__(self):
        return '<Track %r>' % self.title
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


class ARIMAParams(db.Model):
    """Create a data model for the database to be set up for capturing ARIMA parameters
    """
    CURRENCY = db.Column(db.TEXT, primary_key=True)
    P = db.Column(db.INTEGER, unique=False)
    D = db.Column(db.INTEGER, unique=False)
    Q = db.Column(db.INTEGER, unique=False)

    def __repr__(self):
        return '<ARIMA Params %r>' % self.CURRENCY