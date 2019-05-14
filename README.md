# Example project repository

<!-- toc -->

- [Project Charter](#project-charter)
- [Backlog](#backlog)
- [Repo structure](#repo-structure)
- [Documentation](#documentation)
- [Running the application](#running-the-application)
  * [1. Set up environment](#1-set-up-environment)
    + [With `virtualenv` and `pip`](#with-virtualenv-and-pip)
    + [With `conda`](#with-conda)
  * [2. Initialize the database](#2-initialize-the-database)
  * [3. Acquire/ingest the source data](#3-acquireingest-the-source-data)
- [Testing](#testing)

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
│   ├── __init__.py                   <- Initializes the Flask app and database connection
│
├── config                            <- Directory for yaml configuration files for model training, scoring, etc
│   ├── logging/                      <- Configuration files for python loggers
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── archive/                      <- Place to put archive data is no longer usabled. Not synced with git. 
│   ├── raw/                          <- Raw data from external data sources, will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── docs                              <- A default Sphinx project; see sphinx-doc.org for details.
│
├── figures                           <- Generated graphics and figures to be used in reporting.
│
├── models                            <- Trained model objects (TMOs), model predictions, and/or model summaries
│   ├── archive                       <- No longer current models. This directory is included in the .gitignore and is not tracked by git
│
├── notebooks
│   ├── develop                       <- Current notebooks being used in development.
│   ├── deliver                       <- Notebooks shared with others. 
│   ├── archive                       <- Develop notebooks no longer being used.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports and helper functions. 
│
├── src                               <- Source data for the project 
│   ├── archive/                      <- No longer current scripts.
│   ├── helpers/                      <- Helper scripts used in main src files 
│   ├── sql/                          <- SQL source code
│   ├── create_dataset.py             <- Script for creating a (temporary) MySQL database 
│   ├── acquire_data.py               <- Script for ingesting data from different sources 
│   ├── generate_features.py          <- Script for cleaning and transforming data and generating features used for use in training and scoring.
│   ├── train_model.py                <- Script for training machine learning model(s)
│   ├── score_model.py                <- Script for scoring new predictions using a trained model.
│   ├── postprocess.py                <- Script for postprocessing predictions and model results
│   ├── evaluate_model.py             <- Script for evaluating model performance 
│
├── test                              <- Files necessary for running model tests (see documentation below) 

├── run.py                            <- Simplifies the execution of one or more of the src scripts 
├── app.py                            <- Flask wrapper for running the model 
├── config.py                         <- Configuration file for Flask app
├── requirements.txt                  <- Python package dependencies 
```
This project structure was partially influenced by the [Cookiecutter Data Science project](https://drivendata.github.io/cookiecutter-data-science/).


## Running the application 
### 1. Set up environment 

The `requirements.txt` file contains the packages required to run the model code. An environment can be set up in two ways. 

#### With `virtualenv`

```bash
pip install virtualenv

virtualenv pennylane

source pennylane/bin/activate

pip install -r requirements.txt

```
#### With `conda`

```bash
conda create -n pennylane python=3.7
conda activate pennylane
pip install -r requirements.txt

```

### 2. Initialize the database 

1. You can create either a mysql database in RDS OR a SQLITE database locally.
2. To create a mysql database in RDS instance:

    a. Within the project directory, open config/dbconfig.yml.
    
    b. The host, port, user_env, password_env and dbname will need to be changed appropriately to the credentials corresponding the RDS instance where you want the mysql database created.
    
    c. Go to the project directory and run:

    `python run.py create_db`

3. (Optional) To create a SQLITE database locally (instead of RDS):

    a. Within the project directory, open config.py
    
    b. Set DBCONFIG = None
    
    c. The location where the SQLITE database will be created locally is default set in the config DB_PATH. It is default set to the "data" directory within the project repository with the database name as "XchangeRatePredictor.db". Change that only if required.
    
    d. Go to the project directory and run:
    
    `python run.py create_db`


### 3. Acquire/ingest the source data
1. Within the project directory, open config/model_config.yml.
2. Change the S3_LOCATION and S3_FILE_NAME to the bucket and file name where you would like the source JSON to be dumped.
3. Go to the project directory and run:

    `python run.py acquire`
