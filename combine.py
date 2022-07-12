from time import sleep
from tides import TidesScraper
from windguru import WindguruScraper
import pandas as pd
from tqdm import tqdm
import numpy


class CombinedTasks(object):

    def combine_df(self, df: pd.DataFrame,
                   tides_df: pd.DataFrame) -> pd.DataFrame:
        tides_scraper = TidesScraper()
        windguru_scraper = WindguruScraper()

        day_names = df['DIA|'].unique()
        mix_tide_hour_list = []
        state_list = []
        hour_list = []
        new_hour_list = []
        marea_list = []
        state = ""

        for day in tqdm(day_names):
            if tides_df[day] is not None:
                tides_hour_list = tides_df[day].tolist()

                #format and retrieve lists
                returned_tides_hour_list = tides_scraper.remove_ple_baj(
                    tides_hour_list)
                formated_windguru_hour_list = windguru_scraper.format_hour(
                    df, day)
                formated_tides_hour_list = tides_scraper.format_hour(
                    returned_tides_hour_list)
                returned_tides_hour_list.clear()

                #join lists
                total_hour_list = formated_tides_hour_list + formated_windguru_hour_list
                formated_tides_hour_list.clear()
                formated_windguru_hour_list.clear()

                #sort hours in lists
                sorted_hour_list = sorted(
                    total_hour_list,
                    key=lambda d: tuple(map(int, d.split(":"))))
                total_hour_list.clear()

                #combination of tides and hours list
                for pure_hour in sorted_hour_list:
                    result = next((tide_hour for tide_hour in tides_hour_list
                                   if pure_hour in tide_hour), pure_hour)
                    mix_tide_hour_list.append(result)
                sorted_hour_list.clear()

                #generate state list in order to append to dataframe
                for hour in mix_tide_hour_list:
                    if (("ple" not in hour and "baj" not in hour)
                            and (state != "")):
                        state_list.append(state)
                    elif "ple" in hour:
                        up_hour = str(hour).replace("ple", "")
                        state = ["Bajando hasta las", up_hour]
                        hour_list.append(up_hour)
                    elif "baj" in hour:
                        down_hour = str(hour).replace("baj", "")
                        state = ["Subiendo hasta las", down_hour]
                        hour_list.append(down_hour)
                mix_tide_hour_list.clear()

        for state_element in state_list:
            n = hour_list.index(state_element[1]) + 1
            if state_element[1] in hour_list and n >= 0 and n < len(hour_list):
                element = hour_list[n]
                new_hour_list.append(element)
        d2 = [item[0] for item in state_list]

        df['MAREA|'] = pd.Series(d2)
        df['HORA_MAREA|'] = pd.Series(new_hour_list)

        df['MAREA|'] = df['MAREA|'] + df['HORA_MAREA|']
        df = df.drop('HORA_MAREA|', axis=1)
        returned_df = df[0:len(pd.Series(state_list))]
        returned_df['tabid_0_0_SMER'] = returned_df[
            'tabid_0_0_SMER'].str.replace(r'\([^)]*\)', "", regex=True)
        returned_df['tabid_0_0_DIRPW'] = returned_df[
            'tabid_0_0_DIRPW'].str.replace(r'\([^)]*\)', "", regex=True)
        dayOfWeek = {
            'Mo': 'Lu',
            'Tu': 'Ma',
            'We': 'Mi',
            'Th': 'Ju',
            'Fr': 'Vi',
            'Sa': 'Sa',
            'Su': 'Do'
        }
        returned_df['DIA|'] = returned_df['DIA|'].str.split('([0-9]+)').apply(
            ','.join).str[:-1].str.replace(',', '')
        returned_df['DIA|'] = returned_df['DIA|'].replace(dayOfWeek,
                                                          regex=True)
        returned_df.rename(columns={
            'tabid_0_0_SMER': 'DIRECCION-VIENTO|',
            'tabid_0_0_DIRPW': 'DIRECCION-MAR|',
            'tabid_0_0_PERPW': 'PERIODO|',
            'tabid_0_0_HTSGW': 'ALTURA|'
        },
                           inplace=True)

        returned_df += '|'
        return returned_df