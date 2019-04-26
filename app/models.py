from app import db

db.Model.metadata.reflect(db.engine)


class Tracks(db.Model):
    """Create a data model for the database to be set up for capturing songs

    """
    __table__ = db.Model.metadata.tables['tracks']

    def __repr__(self):
        return '<Track %r>' % self.title
