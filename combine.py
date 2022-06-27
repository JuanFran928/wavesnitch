from tides import TidesScraper 
from windguru import WindguruScraper 
import pandas as pd
class CombinedTasks(object):
    
    def combine_df(self, windguru_df: pd.DataFrame, tides_df: pd.DataFrame) -> pd.DataFrame:
        tides_scraper = TidesScraper()
        windguru_scraper = WindguruScraper()
        
        day_names = windguru_df['day'].unique()
        mix_tide_hour_list = []
        state_list = []
        state = ""
            
        for day in day_names:
            tides_hour_list = tides_df[day].tolist()
            
            #format and retrieve lists
            returned_tides_hour_list = tides_scraper.remove_ple_baj(tides_hour_list)
            formated_windguru_hour_list = windguru_scraper.format_hour(windguru_df, day)
            formated_tides_hour_list = tides_scraper.format_hour(returned_tides_hour_list)
            returned_tides_hour_list.clear()
            
            #join lists
            total_hour_list = formated_tides_hour_list + formated_windguru_hour_list
            formated_tides_hour_list.clear() 
            formated_windguru_hour_list.clear()
            
            #sort hours in lists
            sorted_hour_list = sorted(total_hour_list, key=lambda d: tuple(map(int, d.split(":"))))
            total_hour_list.clear()
            
            #combination of tides and hours list
            for pure_hour in sorted_hour_list:
                result = next((tide_hour for tide_hour in tides_hour_list if pure_hour in tide_hour), pure_hour)
                mix_tide_hour_list.append(result)
            sorted_hour_list.clear()
            
            #generate state list in order to append to dataframe
            for hour in mix_tide_hour_list:
                if (("ple" not in hour and "baj" not in hour) and (state != "")):
                    state_list.append(state)
                elif "ple" in hour:
                    state = "bajando"
                elif "baj" in hour:
                    state = "subiendo"
                    
            mix_tide_hour_list.clear()
            
        windguru_df['sea_state'] = pd.Series(state_list)
        windguru_df = windguru_df[0:len(pd.Series(state_list))]
        return windguru_df