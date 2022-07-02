from tides import TidesScraper
from windguru import WindguruScraper
import pandas as pd


class CombinedTasks(object):

    def combine_df(self, df: pd.DataFrame,
                   tides_df: pd.DataFrame) -> pd.DataFrame:
        tides_scraper = TidesScraper()
        windguru_scraper = WindguruScraper()

        day_names = df['Dia'].unique()
        mix_tide_hour_list = []
        state_list = []
        state = ""

        for day in day_names:
            tides_hour_list = tides_df[day].tolist()

            #format and retrieve lists
            returned_tides_hour_list = tides_scraper.remove_ple_baj(
                tides_hour_list)
            formated_windguru_hour_list = windguru_scraper.format_hour(df, day)
            formated_tides_hour_list = tides_scraper.format_hour(
                returned_tides_hour_list)
            returned_tides_hour_list.clear()

            #join lists
            total_hour_list = formated_tides_hour_list + formated_windguru_hour_list
            formated_tides_hour_list.clear()
            formated_windguru_hour_list.clear()

            #sort hours in lists
            sorted_hour_list = sorted(
                total_hour_list, key=lambda d: tuple(map(int, d.split(":"))))
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
                    state = "Bajando"
                elif "baj" in hour:
                    state = "Subiendo"

            mix_tide_hour_list.clear()

        df['Marea'] = pd.Series(state_list)
        #cleaning data
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
        returned_df['Dia'] = returned_df['Dia'].str.split('([0-9]+)').apply(
            ','.join).str[:-1].str.replace(',', '')
        returned_df['Dia'] = returned_df['Dia'].replace(dayOfWeek, regex=True)
        returned_df.rename(columns={
            'tabid_0_0_SMER': 'Direccion-Viento',
            'tabid_0_0_DIRPW': 'Direccion-Mar',
            'tabid_0_0_PERPW': 'Periodo',
            'tabid_0_0_HTSGW': 'Altura'
        },
                           inplace=True)

        return returned_df