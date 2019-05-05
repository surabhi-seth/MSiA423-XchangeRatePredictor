# from app import db
# from app.models import Track
import argparse
import logging.config
import yaml
import os


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker

from src.helpers.helpers import create_connection, get_session


logger = logging.getLogger(__name__)
logger.setLevel("INFO")

Base = declarative_base()


class Tracks(Base):
    """Create a data model for the database to be set up for capturing songs

    """

    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), unique=False, nullable=False)
    artist = Column(String(100), unique=False, nullable=False)
    album = Column(String(100), unique=False, nullable=True)

    def __repr__(self):
        return '<Track %r>' % self.title


def create_db(args):
    """Creates a database with the data model given by obj:`apps.models.Track`

    Args:
        args: Argparse args - should include args.title, args.artist, args.album

    Returns: None

    """

    engine = create_connection(engine_string=args.engine_string)

    Base.metadata.create_all(engine)

    session = get_session(engine=engine)

    track = Tracks(artist=args.artist, album=args.album, title=args.title)
    session.add(track)
    session.commit()
    logger.info("Database created with song added: %s by %s from album, %s ", args.title, args.artist, args.album)
    session.close()


def add_track(args):
    """Seeds an existing database with additional songs.

    Args:
        args: Argparse args - should include args.title, args.artist, args.album

    Returns:None

    """

    session = get_session(engine_string=args.engine_string)

    track = Tracks(artist=args.artist, album=args.album, title=args.title)
    session.add(track)
    session.commit()
    logger.info("%s by %s from album, %s, added to database", args.title, args.artist, args.album)


if __name__ == '__main__':

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers()

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create", description="Create database")
    sb_create.add_argument("--artist", default="Britney Spears", help="Artist of song to be added")
    sb_create.add_argument("--title", default="Radar", help="Title of song to be added")
    sb_create.add_argument("--album", default="Circus", help="Album of song being added.")
    sb_create.add_argument("--engine_string", default='sqlite:///../data/tracks.db',
                           help="SQLAlchemy connection URI for database")
    sb_create.set_defaults(func=create_db)

    # Sub-parser for ingesting new data
    sb_ingest = subparsers.add_parser("ingest", description="Add data to database")
    sb_ingest.add_argument("--artist", default="Emancipator", help="Artist of song to be added")
    sb_ingest.add_argument("--title", default="Minor Cause", help="Title of song to be added")
    sb_ingest.add_argument("--album", default="Dusk to Dawn", help="Album of song being added")
    sb_ingest.add_argument("--engine_string", default='sqlite:///../data/tracks.db',
                           help="SQLAlchemy connection URI for database")
    sb_ingest.set_defaults(func=add_track)

    args = parser.parse_args()
    args.func(args)
