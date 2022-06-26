from hashlib import new
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from time import sleep
import os, json, calendar, datetime, pandas as pd

from datetime import timedelta

link = "https://www.temperaturadelmar.es/europa/lanzarote/arrecife/tides.html"

# coger forecast y obtener la tabla de mareas
# luego hacerle un append al forecast

# hacer un main.py que hace estas tareas.


class TidesScraper(object):

    def __init__(self):
        # self.driver = webdriver.PhantomJS('./phantomjs')
        options = Options()

        options.add_argument("--headless")
        options.add_argument("window-size=1120x550")
        self.driver = webdriver.Chrome(
            executable_path=r"/usr/bin/chromedriver", options=options)

    def page_is_loaded(self):
        x = self.driver.execute_script("return document.readyState")
        if x == "complete":
            return True
        else:
            return False

    def scrape(self):
        self.driver.get(link)
        horasDict = {}

        sleep(10)
        while self.page_is_loaded():
            s = BeautifulSoup(self.driver.page_source, "html.parser")
            tables = s.find_all("table", class_="table table-bordered")
            horas = []
            for table in tables:
                tablebody = table.find("tbody")
                rows = tablebody.find_all("tr")
                hora = []
                for row in rows:
                    cells = row.find_all("td")
                    for cell in cells:
                        if cell.text == "pleamar" or cell.text == "bajamar":
                            hora.append(cell.text.replace("amar", ""))
                        elif ":" in cell.text:
                            ple_baj = hora.pop()
                            text_to_insert = f"{ple_baj} {cell.text}h"
                            hora.insert(len(hora), text_to_insert)
                horas.append(hora)
                for hora in horas:
                     if len(hora) == 3:
                         hora.append("None")
            for hora in horas:
                horasDict[self.get_day_name(horas.index(hora))] = hora
            self.driver.quit()
            return horasDict
    
    def mareas_to_df(self, dict):
        df = pd.DataFrame(dict)
        return df

        # meterlo en otro metodo, convertir a json
    def mareas_to_json(self, mareas):
        text_file = open("mareas.json", "w")
        text_to_write = json.dumps(mareas)
        text_file.write(text_to_write)
        text_file.close()

    # convertir a dataframe, otro metodo
    def jsonfc_to_df(self):
        df = pd.read_json("mareas.json", orient="records")
        return df

    def df_to_txt(self, df):
        if os.path.exists("mareas.txt"):
            os.remove("mareas.txt")
        with open("mareas.txt", "a") as f:
            dfAsString = df.to_string(header=True, index=False)
            f.write(dfAsString)

    def get_day_name(self, add):
        day = datetime.date.today() + datetime.timedelta(days=add)
        day_matches = {
            "Monday": "Mo",
            "Tuesday": "Tu",
            "Wednesday": "We",
            "Thursday": "Th",
            "Friday": "Fr",
            "Saturday": "Sa",
            "Sunday": "Su",
        }
        day_name = day_matches[day.strftime("%A")]
        day_number = day.strftime("%d")
        day_name_number = day_name + str(int(day_number))
        
        return day_name_number
    
    def remove_ple_baj(self, tides_hour_list):
        returned_tides_hour_list = []
        for tide_hour in tides_hour_list:
            if tide_hour != 'None':
                if "baj"in tide_hour:
                    tide_hour = tide_hour.replace("baj ", "")
                elif "ple" in tide_hour:
                    tide_hour = tide_hour.replace("ple ", "")
                returned_tides_hour_list.append(tide_hour)
        return returned_tides_hour_list
    
    def format_hour(self, tides_hour_list):
        formated_tides_hour_list = [element.replace('h', '') for element in tides_hour_list]
        return formated_tides_hour_list