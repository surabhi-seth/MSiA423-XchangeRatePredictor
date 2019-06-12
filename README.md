# Example project repository

<!-- toc -->

- [Project Charter](#project-charter)
- [Repo structure](#repo-structure)
- [Running the application](#running-the-application)
  * [1. Set up environment](#1-set-up-environment)
  * [2. Initialize the database](#2-initialize-the-database)
  * [3. Acquire/ingest the source data](#3-acquireingest-the-source-data)
  * [4. Train](#4-train)
  * [5. Score](#5-score)
  * [6. Run the webapp](#6-run-the-webapp)
- [Makefile and Testing](#makefile-and-testing)

<!-- tocstop -->

## Project Charter 
**Developer**: Surabhi Seth

**QA**: Rachel Rosenberg

**Vision**: Increase the customer volume using the Bank of Etas (BofE) foreign currency exchange service through an exchange rate predictor which provides a unique value add to the customers and a better overall service experience. 

**Mission**: Build an exchange rate predictor that provides a rate forecast to the BofE customers for the next 7 days and for the 3 top exchange currency pairs.

**Success criteria**: 
1. The Mean Absolute Percentage Error (MAPE) for the rate predictions is less that 15%.
2. There is a 1% increase in the customer volume in 6 months from the time this feature goes live.
  

## Repo structure 

```
├── README.md                         <- You are here
│
├── app
│   ├── static/                       <- CSS, JS files that remain static 
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── models.py                     <- Creates the data model for the database connected to the Flask app 
│   ├── app.py                        <- Initializes the Flask app and database connection
│
├── config                            <- Directory for yaml configuration files for model training, scoring, etc
│   ├── logging/                      <- Configuration files for python loggers
│   ├── dbconfig.yml                  <- YAML config containing RDS connection properties
│   ├── flask_config.py               <- Configurations for the Flask app
│   ├── model_config.yml              <- YAML config for various steps in the pipeline
│
├── data                              <- Folder that contains data used or generated. 
│   ├── archive/                      <- Place to put archive data is no longer usabled. Not synced with git. 
│   ├── raw/                          <- Raw data from external data sources, will be synced with git
│
├── src                               <- Source data for the project 
│   ├── helpers/                      <- Helper scripts used in main src files 
│   ├── create_dataset.py             <- Script for creating a (temporary) MySQL database 
│   ├── acquire_data.py               <- Script for ingesting data from different sources 
│   ├── load_data.py                  <- Script for fetching different data objects required at various points in the workflow.
│   ├── train_model.py                <- Script for training machine learning model(s)
│   ├── score_model.py                <- Script for scoring new predictions using a trained model.
│   ├── evaluate_model.py             <- Script for evaluating model performance 
│
├── test                              <- Files necessary for running tests
│   ├── test_helpers.py               <- Contains all tests
│
├── run.py                            <- Simplifies the execution of one or more of the src scripts 
├── config.py                         <- Configuration file for redirecting to other appropriate config files
├── requirements.txt                  <- Python package dependencies 
├── Makefile                          <- Makefile for the entire pipeline and tests
```
This project structure was partially influenced by the [Cookiecutter Data Science project](https://drivendata.github.io/cookiecutter-data-science/).


## Running the application 
### 1. Set up environment 

The `requirements.txt` file contains the packages required to run the model code. An environment can be set up using virtualenv. 


```bash
pip install virtualenv

virtualenv pennylane

source pennylane/bin/activate

pip install -r requirements.txt

```


### 2. Initialize the database 

A. You can create either a mysql database in RDS OR a SQLITE database locally.

B. To create a mysql database in RDS instance:

    a. Within the project directory, open config/dbconfig.yml.
    
    b. The host, port and dbname will need to be changed appropriately to the credentials corresponding the RDS instance where you want the mysql database created.
    
    c. Set your RDS MYSQL username and password:
    
    export MYSQL_USER = "<your rds mysql username>"
    export MYSQL_PASSWORD = "<your rds mysql password>"
    
    d. Go to the project directory and run:

    `python run.py create_db`

C. (Optional) To create a SQLITE database locally (instead of RDS):

    a. Within the project directory, open config.py
    
    b. Set DBCONFIG = None
    
    c. The location where the SQLITE database will be created locally is set in the config DB_PATH. It is default set to the "data" directory within the project repository with the database name as "XchangeRatePredictor.db". Change that only if required.
    
    d. Go to the project directory and run:
    
    `python run.py create_db`


### 3. Acquire/ingest the source data
A. Within the project directory, open config/model_config.yml.

B. Change the S3_LOCATION and S3_FILE_NAME to the bucket and file name where you would like the source JSON to be dumped.

C. Go to the project directory and run:

`python run.py acquire`

### 4. Train
A. The parameters for training are present in config/model_config.yml. You do not need to change them, unless necessary.

B. To train the model, run:

`python run.py train`

C. The parameters for the most optimal ARIMA models, based on training will be stored, in the databse.


### 5. Score
A. The parameters for scoring are present in config/model_config.yml. You do not need to change them, unless necessary.

B. To generate the predictions, run:

`python run.py score`

C. The predictions will be stored in the database.

### 6. Run the webapp
A. If the RDS database was used for data setup, set your MYSQL environment variables by running the following commands in the terminal:

	export MYSQL_USER = "<your rds mysql username>"
	export MYSQL_PASSWORD = "<your rds mysql password>"
	export MYSQL_HOST = "<your rds mysql host url>" 
	export MYSQL_PORT = "<your rds mysql port>"

B. If instead of RDS, a local SQLITE database was used for data setup, open config/flask_config.py and:

    a. Comment out this line: SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, DATABASE_NAME)
    
    b. Uncomment out this line: #SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)

C. Go to the project directory and run:

`python run.py app`

D. Get the IPv4 Public IP found on the EC2 console. Add ":3000" to this IP address to view the page in the web browser.

## Makefile and Testing
Provided that all the necessary steps for setup of RDS/S3 bucket (as described above) have been undertaken, running the following will sequentially run the pipeline (except running the webapp) AND also execute the automated tests:
 
`make all`

If you only want to run the tests, run:

`make tests`