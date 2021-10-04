from pycoingecko import CoinGeckoAPI
import matplotlib.pyplot as plt
import datetime
import time
import pandas as pd
import pprint

cg = CoinGeckoAPI()

data_storage = "Data_Storage"

#Takes value in form of "dd-mm-yyyy"
def timestamp_to_unix(string):
    split = string.split("-")
    formatted_time = datetime.datetime(int(split[2]), int(split[1]), int(split[0]))
    return time.mktime(formatted_time.timetuple())

def unix_to_timestamp(unix_milleseconds):
    in_seconds = unix_milleseconds//1000
    return datetime.datetime.utcfromtimestamp(in_seconds).strftime('%Y-%m-%d %H:%M:%S')

class Coin_Reconnisance:
    def __init__(self, id):
        self.id = id

    #Pypi will only take unix time
    def get_historical_coin_data(self, from_dd_mm_yyyy, to_dd_mm_yyyy, currency="usd"):
        unix_start = timestamp_to_unix(from_dd_mm_yyyy)
        unix_end = timestamp_to_unix(to_dd_mm_yyyy)
        raw_data = cg.get_coin_market_chart_range_by_id(id=self.id, vs_currency=currency, from_timestamp=unix_start, to_timestamp=unix_end)
        columns = {
            "date": [],
            "market_caps": [],
            "prices": [],
            "volume": []
        }
        for k, v in raw_data.items():
            if k == "market_caps":
                for item in v:
                    columns["market_caps"].append(item[1])
                    columns["date"].append(unix_to_timestamp(item[0])) #Inserts time column only once into df
            elif k == "prices":
                for item in v:
                    columns["prices"].append(item[1])
            else:
                for item in v:
                    columns["volume"].append(item[1])
        df = pd.DataFrame(columns)
        return df

    #Mainly a helper function to help visualize how data is returned by the API
    def get_coin_data_from_a_single_point_in_time(self, dd_mm_yyyy):
        data = cg.get_coin_history_by_id(self.id, dd_mm_yyyy)
        store = [self.id, dd_mm_yyyy, data["market_data"]["current_price"]["usd"], data["market_data"]["market_cap"]["usd"], data["market_data"]["total_volume"]["usd"]]
        for x in store:
            print(x)
        print(type(data))
        pprint.pprint(data)

    #For help at a low level
    def plot_coin_graph(self, from_timestamp, to_timestamp, item_of_interest, currency="usd"):
        #Item of interest is either 'prices' or 'volume'
        data = cg.get_coin_market_chart_range_by_id(id=self.id, vs_currency=currency, from_timestamp=from_timestamp, to_timestamp=to_timestamp)
        if item_of_interest == "prices":
            data_array = data['prices']
            interest = "Prices"
        elif item_of_interest == "volume":
            data_array = data['total_volumes']
            interest = "Volume"
        else:
            print("dont know what data you're looking for")
            return None
        dates = []
        interested_values = []
        for x in range(len(data_array) - 1):
            dates.append((datetime.datetime.utcfromtimestamp((data_array[x][0])/1000)).strftime('%Y-%m-%d-%H'))
            interested_values.append(data_array[x][1])
        plt.plot(dates, interested_values)
        plt.ylabel(interest)
        plt.xlabel('Date')
        plt.show()

    #Lower level version of data getting, possible use for other projects
    def save_coin_info_to_csv(self, from_timestamp, to_timestamp):
        object_price = self.get_historical_coin_data(from_timestamp, to_timestamp, "prices")
        object_volume = self.get_historical_coin_data(from_timestamp, to_timestamp, "volume")

        d = {'date': [], 'price': [], 'volume': []}
        for x in range(len(object_price)):
            d['date'].append(object_price[x][0])
            d['price'].append(object_price[x][1])
            d['volume'].append(object_volume[x][1])
        df = pd.DataFrame(data=d)
        df.to_csv(data_storage + '/' + self.id + "_data.csv")

# Example code (getting bitcoin info from Janurary 1 to April 4
# bitcoin = Coin_Reconnisance("bitcoin")
# test = bitcoin.get_historical_coin_data("01-01-2021", "01-04-2021")