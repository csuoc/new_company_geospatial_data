# Import box

import pandas as pd
import os
import glob
import requests
from dotenv import load_dotenv
from folium import Choropleth, Circle, Marker, Icon, Map
from folium.plugins import HeatMap, MarkerCluster

companies = pd.read_csv("../data/companies_cleaned.csv")
load_dotenv()
token_fsq = os.getenv("token_fsq")

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

def plot_Serious_Business_Exent():

    # Read CSV from SB
    df_bus5 = pd.read_csv("../data/5bus.csv")
    df_daycare5 = pd.read_csv("../data/5daycare.csv")
    df_metro5 = pd.read_csv("../data/5metro.csv")
    df_night_club5 = pd.read_csv("../data/5night club.csv")
    df_pets5 = pd.read_csv("../data/5pets.csv")
    df_starbucks5 = pd.read_csv("../data/5starbucks.csv")
    df_train5 = pd.read_csv("../data/5train.csv")
    df_tram5 = pd.read_csv("../data/5tram.csv")
    df_vegan5 = pd.read_csv("../data/5vegan.csv")

    #Extract coordinates in a separate dataframe from SB
    df_bus5 = df_bus5.explode("type")
    df_daycare5 = df_daycare5.explode("type")
    df_metro5 = df_metro5.explode("type")
    df_night_club5 = df_night_club5.explode("type")
    df_pets5 = df_pets5.explode("type")
    df_starbucks5 = df_starbucks5.explode("type")
    df_train5 = df_train5.explode("type")
    df_tram5 = df_tram5.explode("type")
    df_vegan5 = df_vegan5.explode("type")

    # Read CSV from Exent
    df_bus7 = pd.read_csv("../data/7bus.csv")
    df_daycare7 = pd.read_csv("../data/7daycare.csv")
    df_metro7 = pd.read_csv("../data/7metro.csv")
    df_night_club7 = pd.read_csv("../data/7night club.csv")
    df_pets7 = pd.read_csv("../data/7pets.csv")
    df_starbucks7 = pd.read_csv("../data/7starbucks.csv")
    df_train7 = pd.read_csv("../data/7train.csv")
    df_tram7 = pd.read_csv("../data/7tram.csv")
    df_vegan7 = pd.read_csv("../data/7vegan.csv")

    #Extract coordinates in a separate dataframe from Exent
    df_bus7 = df_bus7.explode("type")
    df_daycare7 = df_daycare7.explode("type")
    df_metro7 = df_metro7.explode("type")
    df_night_club7 = df_night_club7.explode("type")
    df_pets7 = df_pets7.explode("type")
    df_starbucks7 = df_starbucks7.explode("type")
    df_train7 = df_train7.explode("type")
    df_tram7 = df_tram7.explode("type")
    df_vegan7 = df_vegan7.explode("type")

    # Map creation

    sfmap = Map(location = [37.789321, -122.401362], zoom_start = 15)

    #Iteration and markers for Serious Business

    for index, row in df_bus5.iterrows():
        #1. MARKER without icon
        sb = {"location": [37.789321, -122.401362], "tooltip": "Serious Business"}
        #2. ICON
        icon = Icon (
        color="blue",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-briefcase",
        icon_color = "black"
        )
        #3. MARKER
        sb_marker = Marker(**sb, icon = icon, radius = 2)
        #4. ADD
        sb_marker.add_to(sfmap)

    for index, row in df_bus5.iterrows():
        #1. MARKER without icon
        bus = {"location": [row["lat"], row["lon"]], "tooltip": "Bus station"}
        #2. ICON
        icon = Icon (
        color="lightred",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-solid fa-bus",
        icon_color = "black"
        )
        #3. MARKER
        bus_marker = Marker(**bus, icon = icon, radius = 2)
        #4. ADD
        bus_marker.add_to(sfmap)

    for index, row in df_daycare5.iterrows():
        #1. MARKER without icon
        daycare = {"location": [row["lat"], row["lon"]], "tooltip": "Daycare center"}
        #2. ICON
        icon = Icon (
        color="darkblue",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-solid fa-child",
        icon_color = "black"
        )
        #3. MARKER
        daycare_marker = Marker(**daycare, icon = icon, radius = 2)
        #4. ADD
        daycare_marker.add_to(sfmap)

    for index, row in df_metro5.iterrows():
        #1. MARKER without icon
        metro = {"location": [row["lat"], row["lon"]], "tooltip": "Metro station"}
        #2. ICON
        icon = Icon (
        color="red",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-subway",
        icon_color = "black"
        )
        #3. MARKER
        metro_marker = Marker(**metro, icon = icon, radius = 2)
        #4. ADD
        metro_marker.add_to(sfmap)
        
    for index, row in df_night_club5.iterrows():
        #1. MARKER without icon
        night = {"location": [row["lat"], row["lon"]], "tooltip": "Night club"}
        #2. ICON
        icon = Icon (
        color="beige",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-glass",
        icon_color = "black"
        )
        #3. MARKER
        night_marker = Marker(**night, icon = icon, radius = 2)
        #4. ADD
        night_marker.add_to(sfmap)
        
    for index, row in df_pets5.iterrows():
        #1. MARKER without icon
        pets = {"location": [row["lat"], row["lon"]], "tooltip": "Pet grooming"}
        #2. ICON
        icon = Icon (
        color="orange",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-paw",
        icon_color = "black"
        )
        #3. MARKER
        pets_marker = Marker(**pets, icon = icon, radius = 2)
        #4. ADD
        pets_marker.add_to(sfmap)
        
    for index, row in df_starbucks5.iterrows():
        #1. MARKER without icon
        starbucks = {"location": [row["lat"], row["lon"]], "tooltip": "Starbucks"}
        #2. ICON
        icon = Icon (
        color="darkgreen",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-coffee",
        icon_color = "black"
        )
        #3. MARKER
        starbucks_marker = Marker(**starbucks, icon = icon, radius = 2)
        #4. ADD
        starbucks_marker.add_to(sfmap)
        
    for index, row in df_train5.iterrows():
        #1. MARKER without icon
        train = {"location": [row["lat"], row["lon"]], "tooltip": "Train station"}
        #2. ICON
        icon = Icon (
        color="black",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-train",
        icon_color = "white"
        )
        #3. MARKER
        train_marker = Marker(**train, icon = icon, radius = 2)
        #4. ADD
        train_marker.add_to(sfmap)

    for index, row in df_tram5.iterrows():
        #1. MARKER without icon
        tram = {"location": [row["lat"], row["lon"]], "tooltip": "Tram station"}
        #2. ICON
        icon = Icon (
        color="pink",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-train",
        icon_color = "black"
        )
        #3. MARKER
        tram_marker = Marker(**tram, icon = icon, radius = 2)
        #4. ADD
        tram_marker.add_to(sfmap)
        
    for index, row in df_vegan5.iterrows():
        #1. MARKER without icon
        vegan = {"location": [row["lat"], row["lon"]], "tooltip": "Vegan restaurant"}
        #2. ICON
        icon = Icon (
        color="green",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-leaf",
        icon_color = "black"
        )
        #3. MARKER
        vegan_marker = Marker(**vegan, icon = icon, radius = 2)
        #4. ADD
        vegan_marker.add_to(sfmap)

    

    #Iteration and markers for Exent

    for index, row in df_bus7.iterrows():
        #1. MARKER without icon
        exent = {"location": [37.787646, -122.402759], "tooltip": "Exent"}
        #2. ICON
        icon = Icon (
        color="blue",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-briefcase",
        icon_color = "black"
        )
        #3. MARKER
        exent_marker = Marker(**exent, icon = icon, radius = 2)
        #4. ADD
        exent_marker.add_to(sfmap)

    for index, row in df_bus7.iterrows():
        #1. MARKER without icon
        bus = {"location": [row["lat"], row["lon"]], "tooltip": "Bus station"}
        #2. ICON
        icon = Icon (
        color="lightred",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-solid fa-bus",
        icon_color = "black"
        )
        #3. MARKER
        bus_marker = Marker(**bus, icon = icon, radius = 2)
        #4. ADD
        bus_marker.add_to(sfmap)

    for index, row in df_daycare7.iterrows():
        #1. MARKER without icon
        daycare = {"location": [row["lat"], row["lon"]], "tooltip": "Daycare center"}
        #2. ICON
        icon = Icon (
        color="darkblue",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-solid fa-child",
        icon_color = "black"
        )
        #3. MARKER
        daycare_marker = Marker(**daycare, icon = icon, radius = 2)
        #4. ADD
        daycare_marker.add_to(sfmap)

    for index, row in df_metro7.iterrows():
        #1. MARKER without icon
        metro = {"location": [row["lat"], row["lon"]], "tooltip": "Metro station"}
        #2. ICON
        icon = Icon (
        color="red",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-subway",
        icon_color = "black"
        )
        #3. MARKER
        metro_marker = Marker(**metro, icon = icon, radius = 2)
        #4. ADD
        metro_marker.add_to(sfmap)
        
    for index, row in df_night_club7.iterrows():
        #1. MARKER without icon
        night = {"location": [row["lat"], row["lon"]], "tooltip": "Night club"}
        #2. ICON
        icon = Icon (
        color="beige",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-glass",
        icon_color = "black"
        )
        #3. MARKER
        night_marker = Marker(**night, icon = icon, radius = 2)
        #4. ADD
        night_marker.add_to(sfmap)
        
    for index, row in df_pets7.iterrows():
        #1. MARKER without icon
        pets = {"location": [row["lat"], row["lon"]], "tooltip": "Pet grooming"}
        #2. ICON
        icon = Icon (
        color="orange",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-paw",
        icon_color = "black"
        )
        #3. MARKER
        pets_marker = Marker(**pets, icon = icon, radius = 2)
        #4. ADD
        pets_marker.add_to(sfmap)
        
    for index, row in df_starbucks7.iterrows():
        #1. MARKER without icon
        starbucks = {"location": [row["lat"], row["lon"]], "tooltip": "Starbucks"}
        #2. ICON
        icon = Icon (
        color="darkgreen",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-coffee",
        icon_color = "black"
        )
        #3. MARKER
        starbucks_marker = Marker(**starbucks, icon = icon, radius = 2)
        #4. ADD
        starbucks_marker.add_to(sfmap)
        
    for index, row in df_train7.iterrows():
        #1. MARKER without icon
        train = {"location": [row["lat"], row["lon"]], "tooltip": "Train station"}
        #2. ICON
        icon = Icon (
        color="black",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-train",
        icon_color = "white"
        )
        #3. MARKER
        train_marker = Marker(**train, icon = icon, radius = 2)
        #4. ADD
        train_marker.add_to(sfmap)

    for index, row in df_tram7.iterrows():
        #1. MARKER without icon
        tram = {"location": [row["lat"], row["lon"]], "tooltip": "Tram station"}
        #2. ICON
        icon = Icon (
        color="pink",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-train",
        icon_color = "black"
        )
        #3. MARKER
        tram_marker = Marker(**tram, icon = icon, radius = 2)
        #4. ADD
        tram_marker.add_to(sfmap)
        
    for index, row in df_vegan7.iterrows():
        #1. MARKER without icon
        vegan = {"location": [row["lat"], row["lon"]], "tooltip": "Vegan restaurant"}
        #2. ICON
        icon = Icon (
        color="green",
        opacity = 0.6,
        prefix = "fa",
        icon="fa-leaf",
        icon_color = "black"
        )
        #3. MARKER
        vegan_marker = Marker(**vegan, icon = icon, radius = 2)
        #4. ADD
        vegan_marker.add_to(sfmap)
    
    return sfmap