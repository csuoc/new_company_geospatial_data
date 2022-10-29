# Import box

from pymongo import MongoClient
import pandas as pd
import re

# Function to rename columns
def rename_columns(df, old_name, new_name):
    
    """
    This a functions that renames the name of any given columns. Requires three arguments.
    Arguments: dataframe, old name of the column, new name of the column.
    Input: the current column name
    Output: the column renamed
    """
    
    df.rename(columns={f"{old_name}": f"{new_name}"}, inplace=True)
    return df.sample(2)

#Mongo connection
client = MongoClient("localhost:27017")
db = client["Ironhack"]
coll = db.get_collection("companies")
    
#Mongo filter
filt = {"$and": [{"description":{"$regex": ".*gam.*|.*Gam.*"}, "overview":{"$regex": ".*gam.*|.*Gam.*"}, 
                "total_money_raised":{"$regex": "\$.*B|\$.*M"}, "tag_list":{"$regex": ".*gam.*|.*Gam.*"}}]}

proj = {"description":1, "name":1, "_id":0, "description":1, "overview":1, "tag_list":1, "total_money_raised":1, "offices":1, "number_of_employees":1}

df_regex = pd.DataFrame(coll.find(filt,proj))

#Extract coordinates in a separate dataframe
df_regex = df_regex.explode(f"offices")
df_offices = df_regex["offices"].apply(pd.Series)

#Delete repeated "description" column
df_offices.drop(columns="description", inplace=True)

#Concatenate the two tables by axis 1
df_full = pd.concat([df_regex, df_offices], axis = 1)
df_full.drop(columns="offices", inplace=True)

#Display all companies located in USA (biggest population of gamedev companies) and located in San Francisco or New York 
#(major density of gamedev companies in USA)

df_full = df_full[(df_full["country_code"] == "USA") & (df_full["city"] == "San Francisco") | (df_full["city"] == "New York")]

#Delete useless rows

deletecol = ["tag_list", "overview", "address2", "zip_code", "state_code", "country_code"]

for i in deletecol:
    df_full.drop(columns=f"{i}", inplace=True)
    
#Drop NaNs

df_full = df_full.dropna()

#Rename columns

oldname = list(df_full.columns)
newname = ["Name", "Number of employees", "Description", "Total money (in million $)", "Main address", "City", "Latitude", "Longitude"]

for o, n in zip(oldname, newname):
    rename_columns(df_full, o, n)
    
#Extracting only values from total money

df_full["Total money (in million $)"] = df_full["Total money (in million $)"].str.extract(r"(\d{1,}\.\d|\d)")
df_full["Total money (in million $)"] = df_full["Total money (in million $)"].astype(float)

#Sorting by total money

df_full = df_full.sort_values(by="Total money (in million $)", ascending=False)

#Minor fixes

df_full["Number of employees"] = df_full["Number of employees"].astype(int)
df_final = df_full.reset_index(drop=True)

#Export to CSV for further analysis    
df_finalcsv = df_final.to_csv("../data/companies_cleaned.csv", index = False)