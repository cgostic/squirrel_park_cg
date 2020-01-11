# Load packages

import pandas as pd
import altair as alt
import geopandas as gpd
import json
from shapely.geometry import Point, Polygon
from shapely.ops import cascaded_union
import shapely.wkt

# Need to enable this to allow work with larger datasets (https://altair-viz.github.io/user_guide/faq.html)
alt.data_transformers.enable('json')

# source: https://automating-gis-processes.github.io/2017/lessons/L3/point-in-polygon.html

url = 'https://data.cityofnewyork.us/api/views/vfnx-vebw/rows.csv'

squirrel_data = pd.read_csv(url, usecols = ['X', 'Y', 'Unique Squirrel ID', 'Hectare', 'Shift', 'Date',
       'Hectare Squirrel Number', 'Age', 'Primary Fur Color', 'Location', 'Kuks', 'Quaas', 'Moans', 'Running', 'Chasing', 'Climbing', 'Eating',
       'Foraging', 'Approaches', 'Indifferent', 'Runs from', 'Lat/Long'])
# source (data): https://catalog.data.gov/dataset/2018-central-park-squirrel-census-hectare-data

# Replace NaN with "Unknown"
squirrel_data = squirrel_data.fillna(value = "Unknown")
# Convert lat/long column of squirrel data from string to point
squirrel_data["Lat/Long"] = squirrel_data["Lat/Long"].apply(shapely.wkt.loads)

# Load data needed to map data on park map
geojson_filepath = './data/central_park_geo.geojson'

def open_geojson(path):
    """
    Opens a geojson file at "path" filepath
    """
    with open(path) as json_data:
        d = json.load(json_data)
    return d

def get_geopandas_df(path):
    """
    Creates geopandas dataframe from geeojson file 
    at "path" filepath
    """
    open_json = open_geojson(path)
    gdf = gpd.GeoDataFrame.from_features((open_json))
    return gdf

# Create geopandas dataframe from Central Park geoJson file
gdf = get_geopandas_df(geojson_filepath)

gdf.at[list(gdf.query('location == "CPW, W 97 St, West Drive, W 100 St"').index), 'sitename'] = "Central Park West (Zone 1)"
gdf.at[list(gdf.query('location == "CPW, 85 St Transverse, West Drive To 96 St"').index), 'sitename'] = "Central Park West (Zone 2)"
gdf.at[list(gdf.query('location == "West Drive, CPW, 65 St Transverse"').index), 'sitename'] = "Central Park West (Zone 3)"
gdf.at[list(gdf.query('location == "66 St To 72 St, CPW To West Drive"').index), 'sitename'] = "Central Park West (Zone 4)"

# source (code): https://medium.com/dataexplorations/creating-choropleth-maps-in-altair-eeb7085779a1
# source (map data): https://data.cityofnewyork.us/City-Government/Parks-Zones/rjaj-zgq7

# Map 'sitename' from mapping data to location of each squirrel observation
# in 'squirrel_data'
squirrel_data["sitename"] = "not set"

def map_park_site(point):
    """
    Matches point location of observation in squirrel_data to polygon
    in gdf that it lies within. Returns "sitename" of polygon.
    
    Parameters
    ----------
    point
        shapely.point object
    
    Returns
    -------
    string
        sitename value of polygon that point lies within
        
    Examples
    --------
    map_park_site(Point((73, 43)))
    > "Great Lawn"
    -------------
    """
#     print(point)
#     for poly in gdf["geometry"]:
#         if point.within(poly):
#             i = list(gdf['sitename'].loc[gdf['geometry'] == poly])
#             val = i[0]
#             return val
    for row in range(len(gdf["geometry"])):
        if point.within(gdf['geometry'][row]):
            val = gdf['sitename'][row]
            return val

# Map sitename to polygons
squirrel_data['sitename'] = squirrel_data['Lat/Long'].apply(map_park_site)

squirrel_data = pd.merge(gdf, squirrel_data, on = 'sitename')
squirrel_data.columns = [column.replace(' ', '_') for column in list(squirrel_data.columns)]

# Prepare squirrel data to graph squirrel counts by park area
squirrel_total_count = squirrel_data[['sitename','Unique_Squirrel_ID',
                                      'Running', 'Chasing', 'Climbing', 
                                      'Eating', 'Foraging', 'Kuks', 'Quaas',
                                      'Moans', 'Approaches']].groupby('sitename').agg({'Unique_Squirrel_ID':'count',
                                                                                       'Running':'sum', 
                                                                                       'Chasing':'sum', 
                                                                                       'Climbing':'sum',
                                                                                       'Eating':'sum', 
                                                                                       'Foraging':'sum', 
                                                                                       'Kuks':'sum', 
                                                                                       'Quaas':'sum',
                                                                                       'Moans':'sum', 
                                                                                       'Approaches':'sum'}).reset_index()

# source (code): https://medium.com/dataexplorations/creating-choropleth-maps-in-altair-eeb7085779a1

squirrel_total_count['Vocalizations'] = squirrel_total_count['Kuks'] + squirrel_total_count['Quaas'] + squirrel_total_count['Moans'] 
#squirrel_total_count.drop(columns = ['Kuks', 'Quaas', 'Moans'])

squirrel_total_count['Running_or_chasing'] = squirrel_total_count['Running'] + squirrel_total_count['Chasing']
#squirrel_total_count.drop(columns = ['Running', 'Chasing'])

squirrel_total_count['Eating_or_foraging'] = squirrel_total_count['Eating'] + squirrel_total_count['Foraging']
squirrel_total_count = squirrel_total_count.drop(columns = ['Eating', 'Foraging', 'Running', 'Chasing', 'Kuks', 'Quaas', 'Moans'])

squirrel_diff_count = squirrel_data[['sitename',
                                      'Shift',
                                      'Unique_Squirrel_ID',]].groupby(['sitename',
                                                                       'Shift']).count().reset_index()
squirrel_diff_df = squirrel_diff_count.pivot(index = 'sitename', columns = 'Shift', values = 'Unique_Squirrel_ID').reset_index()
squirrel_diff_df['Count_diff (AM - PM)'] = squirrel_diff_df['AM'] - squirrel_diff_df['PM']

squirrel_count = pd.merge(squirrel_total_count, squirrel_diff_df[['sitename','Count_diff (AM - PM)']], on = 'sitename', how = 'left')

# Add shortened sitenames
sitenames = ['Bernard Plgd',"Mariner's Gate Plgd",'The Tarr-Coyne Tots Playground','James Michael Levin Plgd',
 'Bendheim Plgd','Reservoir Running Track & Landscape','Pat Hoffman Friedman Plgd','110th St & Lenox Ave Plgd','Conservatory Garden',
 'Heckscher Plgd','Northwest Corner','Reservoir (Southeast)','Strawberry Fields',"Frawleys' Run",'The Great Hill',
 "Nutter's Battery & Fort Clinton Site",'The Metropolitan Museum Of Art','Wollman Rink','79th St Yard And Summit Rock','Wien Walk And Arsenal',
 'Pilgrim Hill & Conservatory Water','Reservoir (Northeast)','Belvdre. Cstl., Turtle Pond, Shkspr Grdn','Central Park West (Zone 1)',
 'Dairy, Chess & Checkers House, Carousel','Central Park West (Zone 3)','East Meadow','North Of The Arsenal','Cedar Hill',
 'Conservatory Gardens West Landscape','Hallett Nature Sanctuary And Pond','Central Park West (Zone 2)','Central Park West (Zone 4)',
 'Loch Ravine','Wallach Walk And East Green','Reservoir (Northwest)','North Meadow Recreation Center','Ross Pinetum',
 "Great Lawn And Cleopatra's Needle",'Central Park South','Blockhouse One','Sheep Meadow','The Mall And Rumsey Playfield',
 'North Meadow', 'The Pool','Bethesda Terrace','Heckscher Ballfields & Playground', 'The Ramble']
sitename_short = ['Bernard Plgd', "Mariner's Gate Plgd",'T.C.T Plgd', 'J.M.L. Plgd',  'Bendheim Plgd',
    'Res. Running Track', 'P.H.F. Plgd', '110th St. Plgd', 'Cons. Garden', 'Heckscher Plgd', 
    'NW Corner', 'Reservoir SE', 'Strawberry Fields', "Frawleys' Run", 'The Great Hill', 
    "Nutter's Battery", 'The Met', 'Wollman Rink', 'Summit Rock', 'Wien Walk', 'Pilgrim Hill',
    'Reservior NE', 'Turtle Pond Area', 'Central Park W (Z-1)', 'Carousel Area', 'Central Park W (Z-3)', 'E Meadow',
     'N of the Arsenal', 'Cedar Hill', 'Cons. Gardens W.', 'Hallett Nat. Sanc.', 
    'Central Park W (Z-2)', 'Central Park W (Z-4)', 'Loch Ravine', 'Wallach Walk', 'Reservoir NW', 
    'N Meadow Rec. Ctr.', 'Ross Pinetum', 'Great Lawn', 'Central Park S.', 'Blockhouse One', 'Sheep Meadow', 
    'The Mall', 'N Meadow', 'The Pool', 'Bethesda Terrace', 'Hecksher Ballfields', 'The Ramble']

squirrel_count['sitename_short'] = squirrel_count['sitename'].map(dict(zip(sitenames,sitename_short)))

#squirrel_count.to_csv('squirrel_count.csv')
gdf = gdf.merge(squirrel_count, left_on = 'sitename', right_on = 'sitename', how = 'inner').sort_values(by=['Unique_Squirrel_ID'])
choro_json = json.loads(gdf.to_json())
with open('squirrel_plots.json', 'w') as json_file:
    json.dump(choro_json, json_file)
