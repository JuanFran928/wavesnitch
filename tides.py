from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from time import sleep
import pandas as pd
import os

from datetime import timedelta

link = "https://www.temperaturadelmar.es/europa/lanzarote/arrecife/tides.html"

# coger forecast y obtener la tabla de mareas
# luego hacerle un append al forecast

# hacer un main.py que hace estas tareas.


class Scraper(object):
    def __init__(self):
        # self.driver = webdriver.PhantomJS('./phantomjs')
        options = Options()

        options.add_argument("--headless")
        options.add_argument("window-size=1120x550")
        self.driver = webdriver.Chrome(
            executable_path=r"/usr/bin/chromedriver", options=options
        )

    def page_is_loaded(self):
        x = self.driver.execute_script("return document.readyState")
        if x == "complete":
            return True
        else:
            return False

    def scrape(self):
        print("Loading...")
        self.driver.get(link)

        sleep(10)
        while self.page_is_loaded():
            s = BeautifulSoup(self.driver.page_source, "html.parser")
            tables = s.find_all("table", class_="table table-bordered")
            horas = ""
            for table in tables:
                tablebody = table.find("tbody")
                rows = tablebody.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    for cell in cells:
                        if cell.text == "pleamar" or cell.text == "bajamar":
                            horas = horas + str(cell.text) + " "
                        elif ":" in cell.text:
                            horas = horas + str(cell.text) + "hx"
                horas = horas + "-"
            horas = horas.split("-")
            horas = [hora for hora in horas if hora]
            horas = [hora.split("x") for hora in horas]
            horas = [list(filter(None, hora)) for hora in horas]

            print(horas)
            self.driver.quit()
            return horas

        # meterlo en otro metodo, convertir a json

    def forecast_to_json(self, forecast):
        text_file = open("forecast.json", "w")
        text_to_write = str(forecast).replace("'", '"')
        text_file.write(text_to_write)
        text_file.close()

    # convertir a dataframe, otro metodo
    def jsonfc_to_df(self):
        df = pd.read_json("forecast.json", orient="records")

    def df_to_txt(self, df):
        os.remove("prueba.txt")
        with open("prueba.txt", "a") as f:
            dfAsString = df.to_string(header=False, index=False)
            f.write(dfAsString)


if __name__ == "__main__":
    scraper = Scraper()
    forecast = scraper.scrape()
    print(forecast)
    scraper.forecast_to_json(forecast)
    df = scraper.jsonfc_to_df()
    scraper.df_to_txt(df)
