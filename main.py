from mareas import TidesScraper
from windguru import WindguruScraper
import time


if __name__ == "__main__":
    
    print("Scrapping Tides...")
    tides_scraper = TidesScraper()
    mareas = tides_scraper.scrape()
    tides_df = tides_scraper.mareas_to_df(mareas)
    print("Finished Tides...")
    
    print("Scrapping Windguru...")
    windguru_scraper = WindguruScraper()
    forecast = windguru_scraper.scrape()
    windguru_df = windguru_scraper.forecast_to_df(forecast)
    windguru_df = windguru_scraper.conditions(windguru_df)
    print("Finished Windguru...")
    
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
        
        #join only hours lists
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
        
        #generate state list to append to dataframe
        for index, hour in enumerate(mix_tide_hour_list):
            if (("ple" not in hour and "baj" not in hour) and (state != "")):
                state_list.append(state)
            elif "ple" in hour:
                state = "bajando"
            elif "baj" in hour:
                state = "subiendo"
                
        mix_tide_hour_list.clear()

    windguru_df['estado'] = state_list
    windguru_scraper.df_to_txt(windguru_df)