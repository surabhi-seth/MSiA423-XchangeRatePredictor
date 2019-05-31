'''
from app import db
from app.models import Rates
from src.load_data import get_latest_rates
from datetime import datetime, timedelta
import requests
import pandas as pd


def increment_rate_data():
    latest_rates = get_latest_rates();
    start_date = datetime.strptime(latest_rates.DATE[0], '%Y-%m-%d')
    start_date = start_date + timedelta(days=1)
    start_date = start_date.strftime("%Y-%m-%d")

    now = datetime.now()
    end_date = now.strftime("%Y-%m-%d")

    url = "https://api.exchangeratesapi.io/history?start_at=" + start_date + "&end_at=" + end_date + "&base=USD"
    response = requests.get(url)
    result = response.json()

    dates_list = list(result['rates'].keys())
    inputs = {
        'DATE': [date for date in dates_list],
        'EUR': [result['rates'][date]['EUR'] for date in dates_list],
        'INR': [result['rates'][date]['INR'] for date in dates_list],
        'GBP': [result['rates'][date]['GBP'] for date in dates_list]
    }

    rates = pd.DataFrame(data=inputs)
    rates = rates.sort_values(by=['DATE'], ascending=True).reset_index(drop=True)
    db.session.bulk_insert_mappings(Rates, rates.to_dict(orient="records"))
    db.session.commit()
'''