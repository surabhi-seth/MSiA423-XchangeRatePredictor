
${HOME}/pennylane/bin/activate: requirements.txt
	test -d ${HOME}/pennylane || virtualenv ${HOME}/pennylane
		. ${HOME}/pennylane/bin/activate; pip install -r requirements.txt
	touch ${HOME}/pennylane/bin/activate

venv: ${HOME}/pennylane/bin/activate


src/create_dataset.py: config/dbconfig.yml config.py
	. ${HOME}/pennylane/bin/activate; python run.py create_db

create_db: src/create_dataset.py


data/raw/raw_exchange_rates.json: config/model_config.yml
	. ${HOME}/pennylane/bin/activate; python run.py acquire

acquire_rates: data/raw/raw_exchange_rates.json


data/raw/exchange_rates_dl.json: config/model_config.yml
	. ${HOME}/pennylane/bin/activate; python run.py train

train_model: data/raw/exchange_rates_dl.json


data/raw/exchange_rates_dl.json: config/model_config.yml
	. ${HOME}/pennylane/bin/activate; python run.py score

score_model: data/raw/exchange_rates_dl.json


all: venv create_db acquire_rates train_model score_model