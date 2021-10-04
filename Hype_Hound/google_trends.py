import pandas as pd
from pytrends.request import TrendReq
import datetime

pytrends = TrendReq()

data_storage = "Data_Storage"

#Feed the raw hourly data frame into this function to recieve a dataframe with daily values
#Can be used on larger time spans
def create_df_of_daily_averages(dataframe):
    daily = []
    daily_index = []
    indexes = dataframe.index
    daily_popularity, hours = 0, 0
    for index in indexes:
        hours += 1
        daily_popularity += dataframe.loc[index]
        if str(index)[-8:] != '23:00:00':
            pass
        else:
            daily_popularity = daily_popularity/hours
            daily.append(daily_popularity)
            daily_index.append(str(index)[:10])
            daily_popularity, hours = 0, 0
    df = pd.DataFrame(daily, index=daily_index)
    return df

class Google_Reconissance():
    def __init__(self, id):
        self.id = id

    def get_google_data(self, from_dd_mm_yyyy, to_dd_mm_yyyy, hourly_or_daily="hourly", in_unix=False, save=False):
        if in_unix: #Just data cleaning
            from_unix_time = (datetime.datetime.fromtimestamp(from_dd_mm_yyyy)).strftime('%Y-%m-%d-%H')
            to_unix_time = (datetime.datetime.fromtimestamp(to_dd_mm_yyyy)).strftime('%Y-%m-%d-%H')
            year_start, month_start, day_start, hour_start = int(from_unix_time[:4]), int(from_unix_time[5:7]), int(from_unix_time[8:10]), int(from_unix_time[11:13])
            year_end, month_end, day_end, hour_end = int(to_unix_time[:4]), int(to_unix_time[5:7]), int(to_unix_time[8:10]), int(to_unix_time[11:13])
        else:
            year_start, day_start, month_start = int(from_dd_mm_yyyy[-4:]), int(from_dd_mm_yyyy[3:5]), int(from_dd_mm_yyyy[:2])
            year_end, month_end, day_end = int(to_dd_mm_yyyy[-4:]), int(to_dd_mm_yyyy[3:5]), int(to_dd_mm_yyyy[:2])
        df = pytrends.get_historical_interest(keywords=[self.id], year_start=year_start,
                                              month_start=month_start, day_start=day_start,
                                              year_end=year_end, month_end=month_end, hour_end=23, day_end=day_end,
                                              cat=0, geo='', gprop='', sleep=0)
        df = df.rename(columns={self.id:"google_popularity"})
        df = df.reset_index(level="date") #Sets the date value from an array to a column
        if hourly_or_daily == "daily": #Will return dataframe with daily values
            return create_df_of_daily_averages(df)
        if save == True:
            df.to_csv(data_storage + "/" + '{},{}'.format(self.id, str(from_unix_time) + '.csv'))
        return df

    def get_weekly_google_data(self, save=False, timeframe='today 5-y'):
        pytrends.build_payload(kw_list=[self.id], timeframe=timeframe)
        df = pytrends.interest_over_time()
        if save==True:
            df.to_csv(data_storage + "/" + '{},{}'.format(self.id, timeframe + '.csv'))
        return df

#Example
# bitcoin = Google_Reconissance("bitcoin")
# hourly_bitcoin = bitcoin.get_google_data("01-01-2021", "01-02-2021")
# daily_bitcoin = bitcoin.get_google_data("01-01-2021", "01-02-2021", "daily")