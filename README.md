# SMC Scraper

## Setup

Install [`virtualenv`](https://virtualenv.pypa.io/en/stable/installation/) for `python`

    pip install virtualenv

Create a `virtualenv`

    virtualenv venv

Activate a `virtualenv`

    source venv/bin/activate

Install `python` dependencies

    pip install requests
    pip install selenium

Install [webdriver](https://selenium-python.readthedocs.io/installation.html#drivers) for `selenium` based on the browser of your choice


## Run

To run the scraper
    
    python main.py

This should fetch GO# from SPD and cross-check the information from the SMC portal. 
The results should be in a folder with the following layout

    cases/
    |__  cases.csv 
    |__  <GO#>/
          |__ pdf files
        ...
    |__  
