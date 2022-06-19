from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from time import sleep
import pandas as pd
import os

link = "https://tablademareas.com/es/islas-canarias/arrecife-lanzarote"

# coger forecast y obtener la tabla de mareas
# luego hacerle un append al forecast

# hacer un main.py que hace estas tareas.
# coger solo el dia de hoy, poner los mismos dias que en windguru.py


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

            table = s.find("table", id="tabla_mareas")

            tablebody = table.find("tbody")
            rows = tablebody.find_all("tr")

            tabla_mareas_marea = []
            tabla_mareas_dia = []

            for row in rows:

                cells = row.find_all("td")

                for cell in cells:

                    if (
                        cell.has_attr("class")
                        and cell["class"][0] == "tabla_mareas_marea"
                    ) or (
                        cell.has_attr("class")
                        and cell["class"][0] == "tabla_mareas_dia"
                    ):
                        classHtml = cell["class"][0]
                        if cell.find("div", {"class": ["tabla_mareas_marea_hora"]}):
                            valueHora = (
                                cell.find("div", {"class": ["tabla_mareas_marea_hora"]})
                                .text.replace("\n", "")
                                .replace("\t", "")
                            )
                        elif cell.find("div", {"class": ["tabla_mareas_dia_numero"]}):
                            dia = (
                                cell.find("div", {"class": ["tabla_mareas_dia_dia"]})
                                .text.replace("\n", "")
                                .replace("\t", "")
                            )
                            numero_dia = (
                                cell.find("div", {"class": ["tabla_mareas_dia_numero"]})
                                .text.replace("\n", "")
                                .replace("\t", "")
                            )
                            valueDia = dia + numero_dia

                        if "tabla_mareas_dia" == classHtml:
                            tabla_mareas_dia.append(valueDia)
                        elif "tabla_mareas_marea" == classHtml:
                            tabla_mareas_marea.append(valueHora)
                    N = 4
                    subList = [
                        tabla_mareas_marea[n : n + N]
                        for n in range(0, len(tabla_mareas_marea), N)
                    ]
            mareas = {}
            for line in subList:
                key, value = tabla_mareas_dia[subList.index(line)], line[0:]
                mareas[key] = value

            self.driver.quit()
            return mareas

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
