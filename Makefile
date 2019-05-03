.PHONY: tests api venv clean initialize clean-pyc clean-env clean-tests trained-model


pennylane-env/bin/activate: requirements.txt
	test -d pennylane-env || virtualenv pennylane-env
	. pennylane-env/bin/activate; pip install -r requirements.txt
	touch pennylane-env/bin/activate

venv: pennylane-env/bin/activate

data/features/example-features.csv: data/sample/music_data_combined.csv venv
	. pennylane-env/bin/activate; python run.py generate_features --config=config/test_model_config.yml --input=data/sample/music_data_combined.csv --output=data/features/example-features.csv

features: data/features/example-features.csv

models/example-model.pkl: data/features/example-features.csv venv
	. pennylane-env/bin/activate; python run.py train_model --config=config/test_model_config.yml --input=data/features/example-features.csv --output=models/example-model.pkl

trained-model: models/example-model.pkl

app: venv
	. pennylane-env/bin/activate; python run.py app

swagger: venv
	. pennylane-env/bin/activate; python run.py swagger

test: venv
	. pennylane-env/bin/activate; python run.py test

	. pennylane-env/bin/activate; py.test

clean-tests:
	rm -rf .pytest_cache
	rm -r test/model/test/
	mkdir test/model/test
	touch test/model/test/.gitkeep

clean-env:
	rm -r pennylane-env

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	rm -rf .pytest_cache

clean: clean-tests clean-env clean-pyc