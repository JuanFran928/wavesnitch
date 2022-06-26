#!/usr/bin/env python
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.chrome.options import Options
import warnings, os, numpy as np, pandas as pd


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


class WindguruScraper(object):

    def __init__(self):
        # self.driver = webdriver.PhantomJS('./phantomjs')
        options = Options()

        options.add_argument("--headless")
        options.add_argument("window-size=1120x550")
        self.driver = webdriver.Chrome(
            executable_path=r"/usr/bin/chromedriver", chrome_options=options)

    def page_is_loaded(self):
        x = self.driver.execute_script("return document.readyState")
        if x == "complete":
            return True
        else:
            return False

    def scrape(self):
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
                if id in [
                        "tabid_0_0_SMER",
                        "tabid_0_0_dates",
                        "tabid_0_0_HTSGW",
                        "tabid_0_0_DIRPW",
                        "tabid_0_0_PERPW",
                ]:
                    forecast[id] = []
                    for cell in cells:
                        if ("SMER" in id) | ("DIRPW" in id):
                            value = cell.find("span")["title"]
                        else:
                            value = cell.get_text()
                        forecast[id].append(value)
            self.driver.quit()
            return forecast
    
    def forecast_to_df(self, dict):
        df = pd.DataFrame(dict)
        df[['day', 'hour']] = df['tabid_0_0_dates'].str.split('.', 1, expand=True)
        df = df.drop('tabid_0_0_dates', 1)
        df = df[["day", "hour", "tabid_0_0_SMER", "tabid_0_0_DIRPW", "tabid_0_0_PERPW", "tabid_0_0_HTSGW"]]
        return df
        
        
    # meterlo en otro metodo, convertir a json

    def forecast_to_json(self, forecast):
        with open("forecast.json", "w") as text_file:  # with open
            text_to_write = str(forecast).replace("'", '"')
            text_file.write(text_to_write)

    # convertir a dataframe, otro metodo
    def jsonfc_to_df(self):
        df = pd.read_json("forecast.json", orient="records")
        df[['day', 'hour']] = df['tabid_0_0_dates'].str.split('.', 1, expand=True)
        df = df.drop('tabid_0_0_dates', 1)
        df = df[["day", "hour", "tabid_0_0_SMER", "tabid_0_0_DIRPW", "tabid_0_0_PERPW", "tabid_0_0_HTSGW"]]
        return df

    def conditions(self, df):
        wind_direction = df["tabid_0_0_SMER"].str.split(" ", 1).str[0].str
        sea_direction = df["tabid_0_0_DIRPW"].str.split(" ", 1).str[0].str
        strength = df["tabid_0_0_HTSGW"].astype(float)
        period = df["tabid_0_0_PERPW"].astype(float)

        #SEA
        N_SEA = ((sea_direction.contains("N")) & (sea_direction.len() == 1))
        NW_SEA = ((sea_direction.contains("NW")) & (sea_direction.len() == 3))
        NE_SEA = ((sea_direction.contains("NE")) & (sea_direction.len() == 3))

        #WIND
        N_WIND = ((wind_direction.contains("N")) & (wind_direction.len() == 1))
        W_WIND = ((wind_direction.contains("W")) & (wind_direction.len() == 1))
        E_WIND = ((wind_direction.contains("E")) & (wind_direction.len() == 1))
        S_WIND = ((wind_direction.contains("S")) & (wind_direction.len() == 1))
        NW_WIND = ((wind_direction.contains("NW")) &
                   (wind_direction.len() == 3))
        NE_WIND = ((wind_direction.contains("NE")) &
                   (wind_direction.len() == 3))
        SE_WIND = ((wind_direction.contains("SE")) &
                   (wind_direction.len() == 3))
        SW_WIND = ((wind_direction.contains("SW")) &
                   (wind_direction.len() == 3))

        #STRENGTH
        STRENGTH = ((strength > 1) & (strength < 2))

        #PERIOD
        PERIOD = (
            period > 7
        )  #fijarme en el periodo, más adelante ponerle uno más alto para mejores condiciones

        arrieta_punta_jameos_fariones = (STRENGTH & PERIOD &
                                         (N_SEA & (W_WIND | NW_WIND)))
        caleta_caballo_san_juan = (STRENGTH & PERIOD &
                                   ((N_SEA | NW_SEA) & S_WIND))
        la_santa_izquierda = (STRENGTH & PERIOD & ((NW_SEA | NW_SEA) & E_WIND))
        famara = (STRENGTH & PERIOD & ((NW_SEA | NW_SEA) & SE_WIND))
        san_juan = (STRENGTH & PERIOD & ((N_SEA | NW_SEA) & SW_WIND))
        papagayo_pechiguera = (STRENGTH & PERIOD & (NE_WIND & NW_SEA))

        default = "No hay olas"

        beaches = [
            "Arrieta, Punta, (Viento O Jameos, Viento NW Fariones)",
            "Caleta Caballo, (Mar N-NW San Juan)", "Izquierda de la Santa",
            "Famara papelillo", "San Juan", "Papagayo, Faro, Castillo"
        ]

        df["beach"] = np.select(
            [
                arrieta_punta_jameos_fariones, caleta_caballo_san_juan,
                la_santa_izquierda, famara, san_juan, papagayo_pechiguera
            ],
            beaches,
            default=default,
        )
        return df

    def df_to_txt(self, df):
        if os.path.exists("forecast.txt"):
            os.remove("forecast.txt")
        with open("forecast.txt", "a") as f:
            dfAsString = df.to_string(header=True, index=False)
            f.write(dfAsString)
            
    def df_to_excel(self, df):
        excel = ""
        return excel
    def format_hour(self, windguru_df, day):
        windguru_hour_list = (windguru_df['hour'].loc[windguru_df['day'] == day]).tolist()
        formated_windguru_hour_list = [element.replace('h', ':00') for element in windguru_hour_list]
        return formated_windguru_hour_list


