#!/usr/bin/env python

from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.chrome.options import Options
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


link = 'https://www.windguru.cz/49328'


class Scraper(object):
    def __init__(self):
        #self.driver = webdriver.PhantomJS('./phantomjs')
        options = Options()

        options.add_argument('--headless')
        options.add_argument('window-size=1120x550')
        self.driver = webdriver.Chrome(
            executable_path=r'/usr/bin/chromedriver/chromedriver', chrome_options=options)

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
                        if ('SMER' in id):  # or ('DIRPW' in id):
                            value = cell.find('span')['title']
                        else:
                            value = cell.get_text()
                        forecast[id].append(value)
                        i = i + 1
            
            text_file = open("forecast.json", "w")
            text_to_write = str(forecast).replace("\'", "\"")
            text_file.write(text_to_write)
            text_file.close()
            
            df = pd.read_json('forecast.json',orient='records')
            print(df)
            
            self.driver.quit()
            return forecast


if __name__ == '__main__':
    scraper = Scraper()
    scraper.scrape()




# export PATH="/usr/bin/chromedriver:$PATH"

'''
smer -> direccion viento
tabid_0_0_dates -> fechas
htsgw -> tamaño ola

playa

'''