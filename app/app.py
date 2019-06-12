from flask import render_template, request, redirect, url_for
import logging.config
from flask import Flask
from src.create_dataset import Predictions
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask application
app = Flask(__name__)

# Configure flask app from config.py
app.config.from_pyfile('../config/flask_config.py')

logger = logging.getLogger("xchangeratepred")

# Initialize the database
db = SQLAlchemy(app)


@app.route('/')
def index():
    """Main view that lists the rate predictions.
    Create view into index page that uses data queried from rates database.
    Returns: rendered html template
    """

    try:
        preds = db.session.query(Predictions).limit(100).all()
        logger.info("Index page accessed")
        return render_template('index.html', predictions=preds)
    except:
        logger.warning("Not able to display tracks, error page returned")
        return render_template('error.html')

