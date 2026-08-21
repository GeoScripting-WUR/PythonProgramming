import geopandas as gpd

gdf = gpd.read_file('https://raw.githubusercontent.com/GeoScripting-WUR/PythonProgramming/master/data/gadm41_NLD_2.json')

# Using the dutch coodinate reference system RDNew (epsg code 28992)
crs = ccrs.epsg(28992)

# The data is in another projection as our plot, reprojection to RDnew
gdf = gdf.to_crs(28992)

# Initiate the plot, a little bigger then before
fig = plt.figure(figsize=(15, 15))
ax = plt.subplot(1, 1, 1, projection=crs)
ax.set_title('The municipalities of NL')

# Draw gridlines 
gl = ax.gridlines(
    draw_labels=True, linewidth=2, color='gray', alpha=0.5, linestyle='--'
)

# Set the extent to the extent of the municipalities
min_x, max_x, min_y, max_y = gdf.total_bounds
ax.set_extent((min_x, max_x, min_y, max_y), crs=crs)

# ax.set_extent(gdf.total_bounds, crs=crs) would do this in one step, 
# but the coordinates can be defined seperately as well in this order! 

# Add the geometries to the map
ax.add_geometries(gdf["geometry"], crs=crs, edgecolor = 'black', facecolor = 'None')

plt.show()

import contextily as cx

# add_basemap fetches tiles for the current extent of ax, and reprojects
# them on the fly to whatever crs we give it
cx.add_basemap(ax, crs=crs, zorder=-1)

plt.show()