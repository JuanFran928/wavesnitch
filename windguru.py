#!/usr/bin/env python

from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.chrome.options import Options
import pandas as pd
import warnings
import numpy as np
import os

warnings.filterwarnings("ignore")


link = "https://www.windguru.cz/49328"


class Scraper(object):
    def __init__(self):
        # self.driver = webdriver.PhantomJS('./phantomjs')
        options = Options()

        options.add_argument("--headless")
        options.add_argument("window-size=1120x550")
        self.driver = webdriver.Chrome(
            executable_path=r"/usr/bin/chromedriver", chrome_options=options
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

        forecast = {}
        sleep(10)
        while self.page_is_loaded():
            s = BeautifulSoup(self.driver.page_source, "html.parser")

            table = s.find("table", class_="tabulka")
            tablebody = table.find("tbody")
            rows = tablebody.find_all("tr")

            for row in rows:
                cells = row.find_all("td")
                id = row["id"]
                i = 0
                if id in [
                    "tabid_0_0_SMER",
                    "tabid_0_0_dates",
                    "tabid_0_0_HTSGW",
                    "tabid_0_0_DIRPW",
                ]:
                    forecast[id] = []
                    for cell in cells:
                        if ("SMER" in id) | ("DIRPW" in id):
                            value = cell.find("span")["title"]
                        else:
                            value = cell.get_text()
                        forecast[id].append(value)
                        i = i + 1

            self.driver.quit()
            return forecast

    # meterlo en otro metodo, convertir a json

    def forecast_to_json(self, forecast):
        text_file = open("forecast.json", "w")
        text_to_write = str(forecast).replace("'", '"')
        text_file.write(text_to_write)
        text_file.close()

    # convertir a dataframe, otro metodo
    def jsonfc_to_df(self):
        df = pd.read_json("forecast.json", orient="records")

        return df

    def conditions(self, df):
        wind = df["tabid_0_0_SMER"].str.split(" ", 1).str[0].str

        m1 = (wind.len() == 3) & (wind.contains("NW"))
        m2 = (wind.len() == 3) & (wind.contains("NE"))
        m3 = (wind.len() == 1) & (wind.contains("S"))
        m4 = (wind.len() == 1) & (wind.contains("E"))
        m5 = (wind.len() == 1) & (wind.contains("W"))
        m6 = (wind.len() == 3) & (wind.contains("SE"))
        m7 = (wind.len() == 3) & (wind.contains("SW"))

        vals = [
            "Arrieta, Punta Mujeres",
            "Papagayo, Faro Pechiguera",
            "Caleta Caballo, Famara",
            "La Santa",
            "Playa Honda, Costa Teguise, Fariones",
            "Caleta Caballo, Famara, La Santa",
            "Caleta Caballo, Famara, Norte puro",
        ]

        default = "nothing"

        df["playas"] = np.select([m1, m2, m3, m4, m5, m6, m7], vals, default=default)
        return df

        # Condiciones #https://www.surfmarket.org/es/olas/europa/canarias/lanzarote/

    def df_to_txt(self, df):
        if os.path.exists("prueba.txt"):
            os.remove("prueba.txt")
        with open("prueba.txt", "a") as f:
            dfAsString = df.to_string(header=False, index=False)
            f.write(dfAsString)

    def df_to_excel(self, df):
        excel = ""
        return excel


if __name__ == "__main__":
    scraper = Scraper()
    forecast = scraper.scrape()
    scraper.forecast_to_json(forecast)
    df = scraper.jsonfc_to_df()
    df = scraper.conditions(df)

    scraper.df_to_txt(df)
