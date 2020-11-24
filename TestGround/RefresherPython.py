#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geoscripting 2020
Lesson 10 - Python Refresher
v20201124
CHappyhill
"""
import os
if not os.path.exists('data'): os.makedirs('data')
if not os.path.exists('output'): os.makedirs('output')

import seaborn as sns

# Set layout
sns.set(context='notebook', # Set type of layout
        style='whitegrid', # Set grid style
        palette='colorblind', # Set colors of graph
        font='Garuda',  # Set font type
        font_scale=2) # Set font size

# Load the iris dataset
iris = sns.load_dataset("iris")

# Plot sepal width as a function of sepal_length across days
g = sns.lmplot(x="sepal_length", # Define x-axis data from dataframe
               y="sepal_width", # Define y-axis data from dataframe
               hue="species", # Define groups with data from dataframe
               data=iris,  # Define dataframe               
               fit_reg=True, # Show linear regression
               truncate=True, # Truncate the linear regressions
               height=10, # Define size of graph
               markers=["o", "x", "s"], # Define types of markers
               scatter_kws={"s": 150}, # Define size of markers
               legend_out=False) # Define if legend should be in or out graph

g.ax.legend(loc=4) # Put legend at right bottom corner
g.ax.set_title("Sepal Width as a Function of Sepal Length across Days") # Set title of plot

# Use more informative axis labels than are provided by default
g.set_axis_labels("Sepal length (mm)", "Sepal width (mm)")
g

import folium
import geopandas as gpd
from pyproj import Proj, Transformer, transform
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService 
from folium.plugins import MeasureControl
from folium.raster_layers import ImageOverlay
from folium.vector_layers import PolyLine

## Set coordinates in RD_New and convert them to WGS84
## based on https://pyproj4.github.io/pyproj/stable/gotchas.html#upgrading-to-pyproj-2-from-pyproj-1
x, y = 174094, 444133
xmin, xmax, ymin, ymax = x-450, x+450, y-750, y+450
transformer = Transformer.from_crs(28992, 4326) # define a transformer object
min_lat, min_lon = transformer.transform(xmin, ymin) # mind the swap in axis order, see: https://geopandas.org/projections.html#the-axis-order-of-a-crs
max_lat, max_lon = transformer.transform(xmax, ymax)
avg_lat, avg_lon = transformer.transform(x, y)

# Download infrared orthophoto near Wageningen Campus
url = 'https://geodata.nationaalgeoregister.nl/luchtfoto/infrarood/wms?&request=GetCapabilities'
wms = WebMapService(url, version='1.3.0')
image = wms.getmap(layers=['Actueel_ortho25IR'], styles=['default'], srs='EPSG:28992',
                   bbox=(xmin, ymin, xmax, ymax), size=(200, 200), format='image/png')
imageFilename = 'data/WUR_Infrared_Orthophoto.png'
with open(imageFilename, 'wb') as file:
    file.write(image.read())

# Download roads around Wageningen Campus
WfsUrl = 'https://geodata.nationaalgeoregister.nl/nwbwegen/wfs?'
wfs = WebFeatureService(url=WfsUrl, version='2.0.0')
layer = list(wfs.contents)[0]
xmin, xmax, ymin, ymax = x-1000, x+350, y-1000, y+350
response = wfs.getfeature(typename=layer, bbox=(xmin, ymin, xmax, ymax))
with open('data/Roads.gml', 'wb') as file:
    file.write(response.read())

# Create basemaps: OpenStreetMap, Stamen Toner, Stamen Terrain, Stamen Watercolor
wageningenMap = folium.Map(location=[avg_lat, avg_lon], tiles = 'OpenStreetMap', zoom_start = 15)
folium.TileLayer('Stamen Toner').add_to(wageningenMap)
folium.TileLayer('Stamen Terrain').add_to(wageningenMap)
folium.TileLayer('Stamen Watercolor').add_to(wageningenMap)

# Create layer, add point markers and add layer to map
POILayer = folium.FeatureGroup(name="Points of interest in Wageningen")
POILayer.add_child(folium.Marker([51.987384, 5.666505], popup='Gaia Entrance at Wageningen University Campus',
                                 icon=folium.Icon(color='green',icon='university',prefix='fa')))
POILayer.add_child(folium.Marker([51.978761, 5.663023], popup='Shopping center Tarthorst',
                                 icon=folium.Icon(color='red', icon='fa-shopping-cart', prefix='fa')))
wageningenMap.add_child(POILayer)

# Load road features, transform coordinates to WGS84, create layer and add polyline  with GeoJson function
# folium.GeoJson is general function to plot either points, lines or polygons from a JSON.
# Folium has other ways to plot polygons, such as Polygon() and Chloropeth().
roads = gpd.GeoDataFrame(gpd.read_file('data/Roads.gml'))
roads = roads.to_crs(epsg=4326) # reproject to WGS84
RoadsLayer = folium.FeatureGroup(name="Roads")
RoadsLayer.add_child(folium.GeoJson(roads, style_function=lambda feature:{
        'fillColor': 'blue',    
        'fillOpacity': 0.6,
        'weight': 4,
        'color': 'darkblue'
        }))
wageningenMap.add_child(RoadsLayer)

# Create layer, add polyline and add layer to map
RouteLayer = folium.FeatureGroup(name="Route from campus to shopping center")
polylineLocations = [[51.987384, 5.666505], [51.986899, 5.666848], [51.985501, 5.661650], 
                     [51.981741, 5.664579], [51.979521, 5.664321], [51.979455, 5.663795],
                     [51.979078, 5.663753], [51.978761, 5.663023]]
RouteLayer.add_child(PolyLine(locations=polylineLocations, popup="Path from Gaia to Shopping Center", 
                              color="red", weight=2.5, opacity=1))
wageningenMap.add_child(RouteLayer)

# Overlay raster on top of map
orthophotoLayer = folium.FeatureGroup(name="Infrared Orthophoto of Wageningen")
orthophotoLayer.add_child(ImageOverlay(imageFilename, [[min_lat, min_lon], [max_lat, max_lon]], opacity=0.6))
wageningenMap.add_child(orthophotoLayer)

# Add measurement control and layer control
wageningenMap.add_child(MeasureControl())
wageningenMap.add_child(folium.LayerControl())

# Visualize map
wageningenMap # Jupyter Notebook allows interactive visualization in the Notebook
wageningenMap.save('output/wageningenMap.html') # The folium map can be stored as an HTML file and viewed by opening the HTML file