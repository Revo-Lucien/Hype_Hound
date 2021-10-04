import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from aggregating_data import fetch_all_data_avaliable

'''
Avaliable data:
For files dealing with market fluxuations the avaliable values are ["market_caps", "prices", "volume"]
For files dealing with google trends the avaliable value is ["google_popularity"]

Steps:
Choose if you are pulling new information OR working with pre-existing files
If pulling new information:
    call fetch all data
Else:
    Link any csv you have already called
Visualization functions are avaliable
Ideally clean dataframes with clean_dataframes()
    Current currates data into consistent time intervals that may then be shuffled for better analysis
Run regression on data features of your choosing, data is shuffled and broken between test & train sets
'''

data_path = "../Data_Storage/"

google_file_name, coin_file_name = fetch_all_data_avaliable("ethereum", "01-01-2021", "30-01-2021", data_path)
#OR
# google_file_name, coin_file_name = "file_name", "file_name"

# #Can add nrows= to pd.read_csv() to pull the first nth rows
rows = 100
google = pd.read_csv(data_path+google_file_name, nrows=rows)
coins = pd.read_csv(data_path+coin_file_name, nrows=rows)

lin_reg = LinearRegression()

##############################These functions are mainly for visualizing data #####################################
def extract_key_details_of_dataframe(dataframe, object_of_interest):
    array = dataframe[object_of_interest].to_numpy()
    max_value = np.max(array)
    min_value = np.min(array)
    dates = dataframe["date"]
    return array, max_value, min_value, dates

#Will not work properly if there are null values present
def print_line_with_shade_against_dates(dataframe, object_of_interest):
    object_of_interest, max, min, dates =  extract_key_details_of_dataframe(dataframe, object_of_interest)
    bottom = np.full((1, len(object_of_interest)), min)
    plt.plot(dates, object_of_interest, "b-")
    plt.fill_between(dates, bottom[0], object_of_interest, color='blue', alpha=.2)
    plt.show()

#Select the dataframe you want, then the object of interest must be a column withing that dataframe i.e "prices", "market_caps", etc...
def print_dot_plot_against_dates(dataframe, object_of_interest):
    object_of_interest, max, min, dates = extract_key_details_of_dataframe(dataframe, object_of_interest)
    plt.plot(dates, object_of_interest, "b.")
    plt.show()

##############################For cleaning data#####################################

#In the case that you want to have data indexed at every hour, not all information.
def df_of_structured_timestamps(structured_df, unstructured_df, ):
    structured_dates = structured_df["date"]
    unstructured_dates = unstructured_df["date"]
    market_caps = []
    prices = []
    volume = []
    unstr_pos = 0
    value_was_present = False
    for str_row in range(len(structured_dates)):
        for unstr_row in range(unstr_pos, len(unstructured_dates)):
            str_date = structured_dates[str_row][:13]
            unstr_date = unstructured_dates[unstr_row][:13]
            if str_date == unstr_date:
                market_caps.append(unstructured_df["market_caps"][unstr_row])
                prices.append(unstructured_df["prices"][unstr_row])
                volume.append(unstructured_df["volume"][unstr_row])
                unstr_pos = unstr_row
                value_was_present = True
        if value_was_present is False:
            market_caps.append(None)
            prices.append(None)
            volume.append(None)
        value_was_present = False
    data = {
        "date": structured_dates,
        "market_caps": market_caps,
        "prices": prices,
        "volume": volume
    }
    df = pd.DataFrame(data=data)
    return df

# Necessary data cleaning for comparing two non-time-related features
def remove_null_rows(dataframe, accompanying_df):
    non_time_column = dataframe.iloc[:, 2]
    null_rows = []
    for row in range(len(non_time_column)):
        if np.isnan(non_time_column[row]):
            null_rows.append(row)
    dataframe = dataframe.drop(null_rows)
    accompanying_df = accompanying_df.drop(null_rows)
    return dataframe, accompanying_df

# structured_df will be the dataframe with consistintly placed timestamps, unstructured is what you will attempt to fit to that structure
def clean_dataframes(structured_df, unstructured_df):
    now_structured_data = df_of_structured_timestamps(structured_df, unstructured_df)
    clean_coins, clean_google = remove_null_rows(now_structured_data, structured_df)
    clean_coins = clean_coins.reset_index(drop=True)
    clean_google = clean_google.reset_index(drop=True)
    return clean_google, clean_coins

#Each object must be a column in its respective dataframe
def regression(first_df, second_df, first_object, second_object, shuffle_data=True):
    data = {
        first_object: first_df[first_object],
        second_object: second_df[second_object]
    }
    working_data = pd.DataFrame(data=data)

    if shuffle_data:
        working_data = shuffle(working_data)

    ind_ft_title, dp_ft_title = working_data.keys()
    independent_feature = working_data[first_object]
    dependent_feature = working_data[second_object]

    independent_train, independent_test, dependent_train, dependent_test = train_test_split(independent_feature, dependent_feature, test_size=0.2)

    independent_train = independent_train.to_numpy()
    independent_test = independent_test.to_numpy()
    dependent_train = dependent_train.to_numpy()
    dependent_test = dependent_test.to_numpy()

    independent_train = independent_train[:, np.newaxis]
    independent_test = independent_test[:, np.newaxis]
    dependent_train = dependent_train[:, np.newaxis]
    dependent_test = dependent_test[:, np.newaxis]

    lin_reg.fit(independent_train, dependent_train)

    print("Coefficient of the regression line:\n", str(lin_reg.coef_))
    print("Intercept of the regression line:\n", str(lin_reg.intercept_))

    training_set_pred = lin_reg.predict(independent_train)
    testing_set_pred = lin_reg.predict(independent_test)

    print("Mean squared error (sum(actual-predicted)^2)/N")
    print("Mean squared error of training set: ", str(mean_squared_error(dependent_train, training_set_pred)))
    print("Mean squared error of testing set: ", str(mean_squared_error(dependent_test, testing_set_pred)))
    print("r^2 score, 1-SSE/TSS, how much regression explains of relationship")
    print("r^2 score of training set: ", str(r2_score(dependent_train, training_set_pred)))
    print("r^2 score of testing set: ", str(r2_score(dependent_test, testing_set_pred)))

    plt.plot(independent_train, dependent_train, "b.")
    plt.plot(independent_test, dependent_test, "g.")
    plt.plot(independent_train, training_set_pred, "r-")
    plt.xlabel(ind_ft_title)
    plt.ylabel(dp_ft_title)
    plt.show()

# example:
# comparing google searches vs market price
# regression(google, coins, "google_popularity", "prices")
# comparing two market features
# regression(coins, coins, "prices", "volume")

#Notes:
# Still need to take care of outliers in datasets as well percentage changes instead of full changes
