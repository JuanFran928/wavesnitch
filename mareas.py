from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from time import sleep

link = 'https://tablademareas.com/es/islas-canarias/arrecife-lanzarote'

#coger forecast y obtener la tabla de mareas
#luego hacerle un append al forecast

#hacer un main.py que hace estas tareas.


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

        forecast = {}
        sleep(10)
        while self.page_is_loaded():
            s = BeautifulSoup(self.driver.page_source, "html.parser")

            table = s.find("table", id_="tabla_mareas")
            print(table)
            '''
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

            self.driver.quit()'''
            return table
        
if __name__ == '__main__':
    scraper = Scraper()
    forecast = scraper.scrape()
    print(forecast)
    #scraper.forecast_to_json(forecast)
    #df = scraper.jsonfc_to_df()
    #scraper.df_to_txt(df)