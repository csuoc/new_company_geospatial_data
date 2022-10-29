# Import box

from pymongo import MongoClient
import pandas as pd
import time

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


def clean_table():

    #Mongo connection
    client = MongoClient("localhost:27017")
    db = client["Ironhack"]
    coll = db.get_collection("companies")
    
    #Mongo filter
    filt = {"$and": [{"description":{"$regex": ".*gam.*|.*Gam.*"}, "overview":{"$regex": ".*gam.*|.*Gam.*"}, 
                    "total_money_raised":{"$regex": "\$.*B|\$.*M"}, "tag_list":{"$regex": ".*gam.*|.*Gam.*"}}]}

    proj = {"description":1, "name":1, "_id":0, "description":1, "overview":1, "tag_list":1, "total_money_raised":1, "offices":1, "number_of_employees":1}

    df_regex = pd.DataFrame(coll.find(filt,proj))

    # Extract coordinates in a separate dataframe
    df_regex = df_regex.explode(f"offices")
    df_offices = df_regex["offices"].apply(pd.Series)

    #Delete repeated "description" column
    df_offices.drop(columns="description", inplace=True)

    #Concatenate the two tables by axis 1
    df_full = pd.concat([df_regex, df_offices], axis = 1)
    df_full.drop(columns="offices", inplace=True)
    
    return df_full

