import pandas as pd
from google_trends import Google_Reconissance
from coin_prices import Coin_Reconnisance
from twitter_api import Twitter_Reconissance

data_path = "Data_Storage"

#This class has full functionality of all data getting classes
class Full_Aggregation(Coin_Reconnisance, Google_Reconissance, Twitter_Reconissance):
    def __init__(self, id, from_dd_mm_yyyy, to_dd_mm_yyyy):
        self.id = id
        self.from_dd_mm_yyyy = from_dd_mm_yyyy
        self.to_dd_mm_yyyy = to_dd_mm_yyyy

def save_to_csv(df, item, detail, from_dd_mm_yyyy, to_dd_mm_yyyy):
    new_file = "/" + str(item) + "_" + str(detail) + "_" + str(from_dd_mm_yyyy) + "_" + str(to_dd_mm_yyyy) + ".csv"
    complete_path = data_path + new_file
    df.to_csv(complete_path)
    return new_file

#At risk limited storage data_stream can be true to process but not store data
def fetch_all_data_avaliable(item, from_dd_mm_yyyy, to_dd_mm_yyyy, directory, data_stream=False):
    instance = Full_Aggregation(item, from_dd_mm_yyyy, to_dd_mm_yyyy)
    google_information = instance.get_google_data(from_dd_mm_yyyy, to_dd_mm_yyyy)
    coin_information = instance.get_historical_coin_data(from_dd_mm_yyyy, to_dd_mm_yyyy)
    if data_stream == False:
        item_google_title = "/" + str(item) + "_google_" + str(from_dd_mm_yyyy) + "_" + str(to_dd_mm_yyyy) + ".csv"
        item_coin_title = "/" + str(item) + "_coin_" + str(from_dd_mm_yyyy) + "_" + str(to_dd_mm_yyyy) + ".csv"
        google_information.to_csv(directory + item_google_title)
        coin_information.to_csv(directory + item_coin_title)
        return item_google_title, item_coin_title

# Example code:
# bitcoin = Full_Aggregation("bitcoin", "01-01-2021", "01-04-2021")
# daily_bitcoin_google = bitcoin.get_google_data("01-01-2021", "01-04-2021")
# daily_bitcoin_coin = bitcoin.get_historical_coin_data("01-01-2021", "01-04-2021")
# Returns pandas dataframe, with "dd_mm_yyyy"
# save_to_csv(daily_bitcoin_google, "bitcoin", "google")
# fetch_all_data_avaliable("ethereum", "01-01-2021", "30-01-2021")