import io
import zipfile

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import requests
import rasterio
from cartopy import crs as ccrs
from rasterio.plot import show
import contextily as cx

# gdf = gpd.read_file('https://raw.githubusercontent.com/GeoScripting-WUR/PythonProgramming/master/data/gadm41_NLD_2.json')

# # Using the dutch coodinate reference system RDNew (epsg code 28992)
# crs = ccrs.epsg(28992)

# # The data is in another projection as our plot, reprojection to RDnew
# gdf = gdf.to_crs(28992)

# # Add an attribute with the area of each municipality. RDNew (28992) is a
# # projected CRS in meters, so .area gives square meters straight away
# gdf['area_km2'] = gdf.geometry.area / 1_000_000

# # Categorize the areas into 10 equal-width classes, one per municipality
# gdf['area_class'] = pd.cut(gdf['area_km2'], bins=10)

# # Initiate the plot, a little bigger then before
# fig = plt.figure(figsize=(15, 15))
# ax = plt.subplot(1, 1, 1, projection=crs)
# ax.set_title('The municipalities of NL')

# # Draw gridlines 
# gl = ax.gridlines(
#     draw_labels=True, linewidth=2, color='gray', alpha=0.5, linestyle='--'
# )

# # Set the extent to the extent of the municipalities
# min_x, max_x, min_y, max_y = gdf.total_bounds
# ax.set_extent((min_x, max_x, min_y, max_y), crs=crs)

# # ax.set_extent(gdf.total_bounds, crs=crs) would do this in one step, 
# # but the coordinates can be defined seperately as well in this order! 

# # Color each municipality by its area class. add_geometries can't do this
# # (one edgecolor/facecolor for the whole collection), so we use
# # GeoDataFrame.plot() instead - it works directly on a GeoAxes when the
# # data's CRS matches the axes' projection, and it builds a legend for us
# # when given a categorical column
# gdf.plot(
#     ax=ax,
#     column='area_class',
#     categorical=True,
#     legend=True,
#     cmap='viridis',
#     edgecolor='black',
#     legend_kwds={'loc': 'lower right', 'title': 'Municipality area (km²)', 'fontsize': 8},
# )

# # add_basemap fetches tiles for the current extent of ax, and reprojects
# # them on the fly to whatever crs we give it
# cx.add_basemap(ax, crs=crs, zorder=-1)

# plt.show()


# ---- Vector legend example (categorical) ----

fig2 = plt.figure(figsize=(15, 15))
ax2 = plt.subplot(1, 1, 1, projection=crs)
ax2.set_title('Municipalities of NL, colored by province')

# GeoDataFrame.plot() works directly on a GeoAxes when the data's CRS
# matches the axes' projection, and (unlike add_geometries) it builds a
# legend for us when we give it a categorical column
gdf.plot(
    ax=ax2,
    column='NAME_1',
    categorical=True,
    legend=True,
    edgecolor='black',
    legend_kwds={'loc': 'lower right', 'title': 'Province', 'fontsize': 8},
)
ax2.set_extent((min_x, max_x, min_y, max_y), crs=crs)

plt.show()


# ---- Raster legend example (continuous colorbar) ----

url = 'https://github.com/GeoScripting-WUR/VectorRaster/releases/download/tutorial-data/landsat8.zip'
resp = requests.get(url, "data.zip")
zf = zipfile.ZipFile(io.BytesIO(resp.content))
zf.extractall('./')

crsUtm = ccrs.epsg(32631)

fig3 = plt.figure(figsize=(15, 15))
ax3 = plt.subplot(1, 1, 1, projection=crsUtm)
ax3.set_title('Landsat 8 - near-infrared band (band 5)')

dataset = rasterio.open('./LC81970242014109LGN00.tif')

# A single band, so each value maps to one color - this is what a
# colorbar visualizes. An RGB composite has no single value to map.
nir = dataset.read(5)

show(nir, transform=dataset.transform, ax=ax3, cmap='viridis')

# show() returns the ax, not the image mappable, but the AxesImage it
# just drew is still available on the ax afterwards
im = ax3.images[0]
fig3.colorbar(im, ax=ax3, label='Digital Number (DN)', shrink=0.7)

plt.show()
