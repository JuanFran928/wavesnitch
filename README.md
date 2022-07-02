# Wavesnitch

Automation script that helps me in the task of interpreting when there are waves, scraping data from two sites, windguru and the one from rising and falling tides.

# steps to put this to work:

Asure you have selenium and google chrome installed on your linux machine.

1. ```git clone this repo```
2. ```cd to folder```
3. ```python -m venv venv```
4. ```source venv/bin/activate```
3. ```pip install -r requirements.txt```
4. ```asure you downloaded chromedriver and its on path (executable_path argument of self.driver property, in windguru.py and tides.py)```
5. ```python main.py```

At the end, it will generate a text file (forecast.txt), where you can see all the conditions.

This project is still under construction

If you enjoyed this project, I will be so much pleased if you give me a star.
