from tides import TidesScraper
from windguru import WindguruScraper
from combine import CombinedTasks
from color import color


if __name__ == "__main__":
    
    print(f"{color.BLUE}Scrapping Tides ...")
    tides_scraper = TidesScraper()
    tides = tides_scraper.scrape()
    tides_df = tides_scraper.mareas_to_df(tides)
    print(f"Finished Tides.{color.END}")
    
    print(f"{color.GREEN}Scrapping Windguru ...")
    windguru_scraper = WindguruScraper()
    forecast = windguru_scraper.scrape()
    windguru_df = windguru_scraper.forecast_to_df(forecast)
    windguru_df = windguru_scraper.conditions(windguru_df)
    print(f"Finished Windguru.{color.END}")
    
    print(f"{color.RED}Combining Data ...")
    combine = CombinedTasks()
    df = combine.combine_df(windguru_df, tides_df)
    print(f"Finished Combining.{color.END}")
    windguru_scraper.df_to_txt(df)

