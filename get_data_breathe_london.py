import requests
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import pyproj
import time

'''
Code to download Breathe London data
'''

api_key = input('API Key: ')

response = requests.get(rf'https://api.breathelondon.org/api/ListSensors?key={api_key}')
#response = requests.get(rf'https://api.breathelondon.org/api/getClarityData/{siteCode}/IPM25/{startDate}/{endDate}/Hourly?key={api_key}')  #can also get INO2 data

# Check if the response status code is OK (200) before attempting to parse JSON.
if response.status_code == 200:
    try:
        # Print the response text to see what it contains.
        #print(response.text)

        # Attempt to parse the response as JSON.
        json_data = response.json()

    except Exception as e:
        print(f"Error parsing JSON: {e}")
else:
    print(f"Request failed with status code: {response.status_code}")

all_sensors = pd.DataFrame(json_data[0])
all_sensors.to_csv(r'/home/doug/git/AirQuality/csv/list_all_sensors.csv', index=False)

geometry = [Point(xy) for xy in zip(all_sensors['Longitude'], all_sensors['Latitude'])]
gdf = gpd.GeoDataFrame(all_sensors, geometry=geometry)

original_crs = 'EPSG:4326'
gdf.crs = original_crs
# Target projection (British National Grid, EPSG:27700)
british_national_grid = 'EPSG:27700'
gdf = gdf.to_crs(british_national_grid)

output_shapefile_path = r'list_all_sensors.shp'
gdf.to_file(output_shapefile_path)

options = ['IPM25', 'INO2']


all_sensors = all_sensors.reset_index() 

startDate = datetime(2024, 1, 1).replace(tzinfo=None)
endDate = datetime(2024, 4, 1).replace(tzinfo=None)

print(startDate.timestamp())

for index, row in all_sensors.iterrows():
    for option in options:
        # convert startdate into correct format

    
        if row['EndDate'] is None:
            endDate = datetime(2024, 4, 1).replace(tzinfo=None)

        elif int(datetime.strptime(row['EndDate'], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()) < int(endDate.timestamp()):
            print('Does not contain full 2023 years data')

        if int(datetime.strptime(row['StartDate'], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()) > int(startDate.timestamp()):
            print('Does not contain full 2022 years data')

        elif row['OverallStatus'] == 'needsAttention' or row['OverallStatus'] =='offline':
            # Ignore offline or needs attention nodes
            print('Offline or Needs Attention')

        else:
            # collect data for healthy nodes
            print(rf"https://api.breathelondon.org/api/getClarityData/{row['SiteCode']}/{option}/{startDate}/{endDate}/Hourly?key={api_key}")
            response = requests.get(rf"https://api.breathelondon.org/api/getClarityData/{row['SiteCode']}/{option}/{startDate}/{endDate}/Hourly?key={api_key}")  #can also get INO2 data

            # Check if the response status code is OK (200) before attempting to parse JSON.
            if response.status_code == 200:
                try:
                    # Print the response text to see what it contains.
                    # Attempt to parse the response as JSON.
                    df = response.json()
                    df = pd.DataFrame(df)

                    # Check if 'DateTime' column exists as some nodes were causing issues as no data was coming through
                    if 'DateTime' in df.columns:
                        # Apply datetime parsing
                        df['DateTime'] = df['DateTime'].apply(lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"))
                        df.to_csv(fr"/home/doug/git/AirQuality/csv/Q1_2024/{row['SiteCode']}_all_data_{option}.csv", index=False)
                    else:
                        print("Error: 'DateTime' column not found in DataFrame.")

                except Exception as e:
                    print(f"Error parsing JSON: {e}")
            else:
                print(f"Request failed with status code: {response.status_code}")

            



    
            