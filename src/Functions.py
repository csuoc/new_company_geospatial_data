# Import box

from pymongo import MongoClient
import pandas as pd
import re
import os
import glob
import requests
from dotenv import load_dotenv

companies = pd.read_csv("../data/companies_cleaned.csv")
load_dotenv()
token_fsq = os.getenv("token_fsq")

def Mongoconnect():
    client = MongoClient("localhost:27017")
    db = client["Ironhack"]
    coll = db.get_collection("companies")
    return coll

def apply_regex():
    """
    Filtering by all industries that contain the strings "Gam/gam"  in their description, overview or tag categories.
    Filtering by all industries that are millionaire or billonaire.
    It returns a filtered pandas dataframe.
    """

    filt = {"$and": [{"description":{"$regex": ".*gam.*|.*Gam.*"}, "overview":{"$regex": ".*gam.*|.*Gam.*"}, 
                    "total_money_raised":{"$regex": "\$.*B|\$.*M"}, "tag_list":{"$regex": ".*gam.*|.*Gam.*"}}]}

    proj = {"description":1, "name":1, "_id":0, "description":1, "overview":1, "tag_list":1, "total_money_raised":1, "offices":1, "number_of_employees":1}

    df_regex = pd.DataFrame(coll.find(filt,proj))

    return df_regex.head()

def extract_coordinates():

    df_regex = df_regex.explode(f"offices")
    df_offices = df_regex["offices"].apply(pd.Series)
    df_offices.drop(columns="description", inplace=True)
    df_full = pd.concat([df_regex, df_offices], axis = 1)
    return df_full.head()

#ANALYSIS

def call_FSQ(category):
    
    categories= {"vegan" : 13377,
                 "daycare" : 11026,
                 "night club" : 10032,
                 "airport" : 19031,
                 "bus" : 19042,
                 "metro" : 19046,
                 "train" : 19047,
                 "tram" : 19050,
                 "basket" : 18006
                }
    lst=[]
    
    for i in range(0,13):
              
        categ = categories[f"{category}"]
        latitude = companies.iloc[i].loc['Latitude']
        longitude = companies.iloc[i].loc['Longitude']

    
        url = f"https://api.foursquare.com/v3/places/search?ll={latitude}%2C{longitude}&categories={categ}&radius=2000&limit=10"

        headers = {"accept": "application/json",
                  "Authorization" : token_fsq}

        response = requests.get(url, headers=headers).json()

        for i in response["results"]:
            name = i["name"]
            distance = i["distance"]
            address =  i["location"]["formatted_address"]
            lat = i["geocodes"]["main"]["latitude"]
            long = i["geocodes"]["main"]["longitude"]
            type_ = {"typepoint": 
                                {"type": "Point", 
                                "coordinates": [lat, long]}}

            lst.append({"name":name, "lat":lat, "lon":long, "distance":distance, "type":type_})

    category = pd.DataFrame(lst)
    category = gpd.GeoDataFrame(category, geometry=gpd.points_from_xy(category["lon"], category["lat"]))
    
    mapa = Map(Layer(category, "color:purple", popup_hover=[popup_element("name", "Restaurants near each location")]), basemap=basemaps.voyager)

    return mapa

def get_tables(row, category, radius):
    
    categories= {"vegan" : 13377,
                 "daycare" : 11026,
                 "night club" : 10032,
                 "airport" : 19037,
                 "bus" : 19042,
                 "metro" : 19046,
                 "train" : 19047,
                 "tram" : 19050,
                 "basket" : 18008,
                 "pets" : 11134
                }
    
    queries= ["vegan restaurant", ""]

    latitude = companies.iloc[row].loc['Latitude']
    longitude = companies.iloc[row].loc['Longitude']
    categ = categories[category]

    url = f"https://api.foursquare.com/v3/places/search?ll={latitude}%2C{longitude}&categories={categ}&radius={radius}&limit=10"

    headers = {"accept": "application/json",
                          "Authorization" : token_fsq}

    response = requests.get(url, headers=headers).json()

    lst=[]
    
    for i in response["results"]:
        name = i["name"]
        distance = i["distance"]
        address =  i["location"]["formatted_address"]
        lat = i["geocodes"]["main"]["latitude"]
        long = i["geocodes"]["main"]["longitude"]
        type_ = {"typepoint": 
                            {"type": "Point", 
                            "coordinates": [lat, long]}}

        lst.append({"name":name, "lat":lat, "lon":long, "distance":distance, "type":type_})

    df = pd.DataFrame(lst)
    df.to_csv(f"../data/{row}{category}.csv", index=False)
        
    pass

def extract_categories(radius):
    
    categories= {"vegan" : 13377,
                 "daycare" : 11026,
                 "night club" : 10032,
                 "airport" : 19037,
                 "bus" : 19042,
                 "metro" : 19046,
                 "train" : 19047,
                 "tram" : 19050,
                 "basket" : 18008,
                 "pets" : 11134
                    }
    for i in range(len(companies)):
        for j in categories.keys():
            get_tables(i, j, radius)
    pass

def calculate_distances(category):
    means = []
    counts = []
    path = os.getcwd()

    for row in range(len(companies)):
        csv_files = glob.glob(os.path.join("../data/", f"{row}{category}.csv"))
        for f in csv_files:
            if os.path.getsize(f) < 100:
                print("These are the csv files without your request:")
                display(f)

            elif os.path.getsize(f) > 100:
                df = pd.read_csv(f)

                means.append(df["distance"].mean())
                counts.append((df["distance"].count()))
    return means, counts

def get_starbucks(row, radius):
    
    
    latitude = companies.iloc[row].loc['Latitude']
    longitude = companies.iloc[row].loc['Longitude']
 
    url = f"https://api.foursquare.com/v3/places/search?query=starbucks&ll={latitude}%2C{longitude}&radius={radius}&limit=10"

    headers = {"accept": "application/json",
                          "Authorization" : token_fsq}

    response = requests.get(url, headers=headers).json()

    lst=[]
    
    for i in response["results"]:
        name = i["name"]
        distance = i["distance"]
        address =  i["location"]["formatted_address"]
        lat = i["geocodes"]["main"]["latitude"]
        long = i["geocodes"]["main"]["longitude"]
        type_ = {"typepoint": 
                            {"type": "Point", 
                            "coordinates": [lat, long]}}

        lst.append({"name":name, "lat":lat, "lon":long, "distance":distance, "type":type_})

    df = pd.DataFrame(lst)
    df.to_csv(f"../data/{row}starbucks.csv", index=False)
        
    pass

def extract_starbucks(radius):
    
    for i in range(len(companies)):
        get_starbucks(i, radius)
    pass

def concat_df():

    lst=[]
    
    path = os.getcwd()
    csv_files = glob.glob(os.path.join("../data/", "7*.csv"))
    
    for f in csv_files:
        if os.path.getsize(f) > 100:
            df = pd.read_csv(f)
            lst.append(df)
            big_df = pd.concat(lst, axis = 0, keys=["first", "second", "third", "fourth", "fifth", "seven"
                                                "eigth", "ninth", "tenth", "eleventh"])
    big_df.to_csv("../data/7United.csv", index=False)

    pass

def roundval(df, column_name, n):
    """
    This is a function that rounds any float to a given n value. Requires three arguments.
    Arguments: dataframe, name of the column where you want to rewrite the values, value of the round
    Input: a float with multiple decimals
    Output: a float with n decimals
    """
    df[f"{column_name}"] = [round(i,n) for i in df[f"{column_name}"]]
    return df.sample(2)