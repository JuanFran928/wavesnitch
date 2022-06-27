from tides import TidesScraper
from windguru import WindguruScraper
from combine import CombinedTasks


if __name__ == "__main__":
    
    print("Scrapping Tides...")
    tides_scraper = TidesScraper()
    tides = tides_scraper.scrape()
    tides_df = tides_scraper.mareas_to_df(tides)
    print("Finished Tides...")
    
    print("Scrapping Windguru...")
    windguru_scraper = WindguruScraper()
    forecast = windguru_scraper.scrape()
    windguru_df = windguru_scraper.forecast_to_df(forecast)
    windguru_df = windguru_scraper.conditions(windguru_df)
    print("Finished Windguru...")
    
    combine = CombinedTasks()
    df = combine.combine_df(windguru_df, tides_df)
    
    windguru_scraper.df_to_txt(df)
