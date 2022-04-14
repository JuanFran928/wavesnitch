#!/usr/bin/env python

from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.chrome.options import Options
import pandas as pd
import warnings
import numpy as np
import os
warnings.filterwarnings('ignore')

#Prueba rebase
#Prueba rebase
link = 'https://www.windguru.cz/49328'

class Scraper(object):
    def __init__(self):
        options = Options()

        options.add_argument('--headless')
        options.add_argument('window-size=1120x550')
        self.driver = webdriver.Chrome(
            executable_path=r'/usr/bin/chromedriver', chrome_options=options)

    def page_is_loaded(self):
        x = self.driver.execute_script("return document.readyState")
        if x == "complete":
            return True
        else:
            return False

    def scrape(self):
        print('Loading...')
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
                id = row['id']
                i = 0
                if id in ['tabid_0_0_SMER', 'tabid_0_0_dates', 'tabid_0_0_HTSGW']:
                    forecast[id] = []
                    for cell in cells:
                        if ('SMER' in id): 
                            value = cell.find('span')['title']
                        else:
                            value = cell.get_text()
                        forecast[id].append(value)
                        i = i + 1

            self.driver.quit()
            return forecast

    # meterlo en otro metodo, convertir a json

    def forecast_to_json(self, forecast):
        text_file = open("forecast.json", "w")
        text_to_write = str(forecast).replace("\'", "\"")
        text_file.write(text_to_write)
        text_file.close()

    # convertir a dataframe, otro metodo
    def jsonfc_to_df(self):
        df = pd.read_json('forecast.json', orient='records')
        
        

        # Condiciones
        df['playa'] = np.where((df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.len() == 3) & (df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.contains('NW')), 'Arrieta, Punta Mujeres',
                               np.where((df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.len() == 3) & (df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.contains('NE')), 'Papagayo, Faro Pechiguera',
                                        np.where((df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.len() == 1) & (df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.contains('S')), 'Caleta Caballo, Famara',
                                                 np.where((df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.len() == 1) & (df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.contains('E')), 'La Santa',
                                                          np.where((df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.len() == 1) & (df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.contains('W')), 'Playa Honda, Costa Teguise, Fariones',
                                                                   np.where((df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.len() == 3) & (df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.contains('SE')), 'Caleta Caballo, Famara, La Santa',
                                                                            np.where((df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.len() == 3) & (df['tabid_0_0_SMER'].str.split(' ', 1).str[0].str.contains('SW')), 'Caleta Caballo, Famara', 'Norte puro')))))))
        return df

    def df_to_txt(self, df):
        os.remove('prueba.txt')
        with open('prueba.txt', 'a') as f:
            dfAsString = df.to_string(header=False, index=False)
            f.write(dfAsString)

    def df_to_excel(self, df):
        excel = ''
        return excel


if __name__ == '__main__':
    scraper = Scraper()
    forecast = scraper.scrape()
    scraper.forecast_to_json(forecast)
    df = scraper.jsonfc_to_df()
    scraper.df_to_txt(df)


# export PATH="/usr/bin/chromedriver:$PATH"

'''
smer -> direccion viento
tabid_0_0_dates -> fechas
htsgw -> tamaño ola

playa
NNE  SUR
NNO NORTE
N = ?
S Caleta caballo, famara
SE caleta caballo, famara, La santa
SO Caleta caballo, famara
E La santa
W Playa honda, costa teguise, arrecife, matagorda

separar dia y hora en columnas
separar grados y sentido en columnas

Poner subida y bajada de la marea, hacer otro script para ello, generar dataframe y luego combinarlos 
'''
