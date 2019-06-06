
${HOME}/pennylane/bin/activate: requirements.txt
	test -d ${HOME}/pennylane || virtualenv ${HOME}/pennylane
	. ${HOME}/pennylane/bin/activate; pip install -r requirements.txt
	touch ${HOME}/pennylane/bin/activate

venv: ${HOME}/pennylane/bin/activate


create_db:
	. ${HOME}/pennylane/bin/activate; python run.py create_db


acquire_rates:
	. ${HOME}/pennylane/bin/activate; python run.py acquire


train_model:
	. ${HOME}/pennylane/bin/activate; python run.py train


score_model:
	. ${HOME}/pennylane/bin/activate; python run.py score


webapp:
	. ${HOME}/pennylane/bin/activate; python run.py app


tests:
	. ${HOME}/pennylane/bin/activate; pytest ./test/test_helpers.py


all: venv create_db acquire_rates train_model score_model tests