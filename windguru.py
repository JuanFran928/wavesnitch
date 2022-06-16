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


link = "https://www.windguru.cz/49328"  # meterle varios links de las distintas playas, para ser más preciso

links = {
    "famara": "https://www.windguru.cz/49328",
    "santa": "https://www.windguru.cz/45391",
    "garita": "https://www.windguru.cz/49325",
    "jameos": "https://www.windguru.cz/49326",
    "playa_blanca": "https://www.windguru.cz/49319",
    "costa": "https://www.windguru.cz/49323",
    "playa_honda": "https://www.windguru.cz/49322",
}


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
        wind_direction = df["tabid_0_0_SMER"].str.split(" ", 1).str[0].str
        sea_direction = df["tabid_0_0_DIRPW"].str.split(" ", 1).str[0].str

        arrieta_punta_crema = (
            (wind_direction.len() == 3)
            & (wind_direction.contains("NW"))
            & (sea_direction.len() == 3)
            & (sea_direction.contains("SE"))
        )

        arrieta_punta = (wind_direction.len() == 3) & (wind_direction.contains("NW"))

        papagayo_pechiguera_crema = (
            (wind_direction.len() == 3)
            & (wind_direction.contains("NE") & sea_direction.len() == 3)
            & (sea_direction.contains("SW"))
        )

        papagayo_pechiguera = (wind_direction.len() == 3) & (
            wind_direction.contains("NE")
        )

        caballo_famara_crema = (wind_direction.len() == 1) & (
            wind_direction.contains("S")
            & (sea_direction.len() == 1)
            & (sea_direction.contains("N"))
        )

        caballo_famara = (wind_direction.len() == 1) & (wind_direction.contains("S"))

        lasanta_crema = (
            (wind_direction.len() == 1)
            & (wind_direction.contains("E"))
            & (sea_direction.len() == 1)
            & (sea_direction.contains("W"))
        )

        lasanta = (wind_direction.len() == 1) & (wind_direction.contains("E"))

        ph_fariones_costa_crema = (
            (wind_direction.len() == 1)
            & (wind_direction.contains("W"))
            & (sea_direction.len() == 1)
            & (sea_direction.contains("E"))
        )

        ph_fariones_costa = (wind_direction.len() == 1) & (wind_direction.contains("W"))

        caballo_famara_santa_crema = (wind_direction.len() == 3) & (
            wind_direction.contains("SE")
            & (sea_direction.len() == 3)
            & (sea_direction.contains("NW"))
        )

        caballo_famara_santa = (wind_direction.len() == 3) & (
            wind_direction.contains("SE")
        )

        caballo_famara_norte_crema = (
            (wind_direction.len() == 3)
            & (wind_direction.contains("SW") & sea_direction.len() == 3)
            & (sea_direction.contains("NE"))
        )

        caballo_famara_norte = (wind_direction.len() == 3) & (
            wind_direction.contains("SW")
        )

        default = "nothing"

        beaches = [
            "Arrieta, Punta Mujeres Cremisima",
            "Arrieta, Punta Mujeres",
            "Papagayo, Faro Pechiguera Cremisima",
            "Papagayo, Faro Pechiguera",
            "Izquierda Caleta Caballo, Famara Cremisima",
            "Izquierda Caleta Caballo, Famara",
            "Izquierda La Santa Cremisima",
            "Izquierda La Santa",
            "Playa Honda, Fariones, Costa Teguise Cremisima",
            "Playa Honda, Fariones, Costa Teguise",
            "Derecha Caleta Caballo, Famara, La Santa Cremisima",
            "Derecha Caleta Caballo, Famara, La Santa",
            "Izquierda Caleta Caballo, Famara, La Santa Cremisima",
            "Izquierda Caleta Caballo, Famara, La Santa",
        ]

        df["playas"] = np.select(
            [
                arrieta_punta_crema,
                arrieta_punta,
                papagayo_pechiguera_crema,
                papagayo_pechiguera,
                caballo_famara_crema,
                caballo_famara,
                lasanta_crema,
                lasanta,
                ph_fariones_costa_crema,
                ph_fariones_costa,
                caballo_famara_santa_crema,
                caballo_famara_santa,
                caballo_famara_norte_crema,
                caballo_famara_norte,
            ],
            beaches,
            default=default,
        )
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
