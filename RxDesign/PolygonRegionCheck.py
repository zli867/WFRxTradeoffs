import os
import sys
import numpy as np
from RxDesign.designUtil import cut_polygon_by_line, generate_continue_region, generate_split_line, find_nearest_point
import matplotlib.pyplot as plt
from shapely.geometry import shape
import json
from util import read_sensing_info, plotPolygons, plotLines
from osgeo import gdal
import pickle
from matplotlib import colors

poly_filename = "/Users/zongrunli/Desktop/Wildfire_GA/RxDesign/temp_polygons/updated_merged_poly_new.pickle"
with open(poly_filename, 'rb') as f:
    polygons_dict = pickle.load(f)

# slope
landfire_file = "/Users/zongrunli/Desktop/Wildfire_GA/data/geo_static/Slope_Clipped.tif"
landfire_ds = gdal.Open(landfire_file, gdal.GA_ReadOnly)
nan_value = landfire_ds.GetRasterBand(1).GetNoDataValue()
slope_value = landfire_ds.ReadAsArray()
slope_value = slope_value.astype(float)
slope_value[slope_value == nan_value] = np.nan
slope_info = read_sensing_info(landfire_ds)
lon, lat = slope_info["crs"](slope_info["X"], slope_info["Y"], inverse=True)

fig, ax = plt.subplots(figsize=(8, 6))
plotPolygons(polygons_dict["polys"], ax, 'red')
plt.pcolor(lon, lat, slope_value)
ax.set_aspect('equal')
plt.colorbar()
plt.axis('off')
plt.title("Slope Degrees (deg)", fontsize=16)
plt.show()


# nlcd file
legend = np.array([0, 11, 12, 21, 22, 23, 24, 31, 41, 42, 43, 51, 52, 71, 72, 73, 74, 81, 82, 90, 95])
leg_str = np.array(
    ['No Data', 'Open Water', 'Perennial Ice/Snow', 'Developed, Open Space', 'Developed, Low Intensity',
     'Developed, Medium Intensity', 'Developed High Intensity', 'Barren Land (Rock/Sand/Clay)',
     'Deciduous Forest', 'Evergreen Forest', 'Mixed Forest', 'Dwarf Scrub', 'Shrub/Scrub',
     'Grassland/Herbaceous', 'Sedge/Herbaceous', 'Lichens', 'Moss', 'Pasture/Hay', 'Cultivated Crops',
     'Woody Wetlands', 'Emergent Herbaceous Wetlands'])

def discrete_cmap():
    cmap = plt.get_cmap("tab20c")
    default_cmaplist = [cmap(i) for i in range(cmap.N)]
    # rearrange order
    cmaplist = []
    # water
    for i in range(0, 2):
        cmaplist.append(default_cmaplist[i])
    # developed region
    for i in range(19, 15, -1):
        cmaplist.append(default_cmaplist[i])
    cmaplist.append((140/255, 108/255, 52/255, 1))
    # crops and vegs
    cmap = plt.get_cmap("viridis", 13)
    default_cmaplist = [cmap(i) for i in range(cmap.N)]
    for i in range(0, len(default_cmaplist)):
        cmaplist.append(default_cmaplist[i])
    print(len(cmaplist))
    print(cmaplist)
    cmap = colors.LinearSegmentedColormap.from_list('Custom cmap', cmaplist, len(cmaplist))
    # cmap.set_over(color=high_value_color, alpha=1.0)
    return cmap


nlcd_file = "/Users/zongrunli/Desktop/Wildfire_GA/data/geo_static/NLCD_Clipped.tif"
nlcd_ds = gdal.Open(nlcd_file, gdal.GA_ReadOnly)
nlcd_value = nlcd_ds.ReadAsArray()
nan_value = nlcd_ds.GetRasterBand(1).GetNoDataValue()
nlcd_info = read_sensing_info(nlcd_ds)
lon, lat = nlcd_info["crs"](nlcd_info["X"], nlcd_info["Y"], inverse=True)
nlcd_value = nlcd_value.astype(float)
nlcd_value[nlcd_value == nan_value] = np.nan

nlcd_value[nlcd_value == 0] = np.nan
for idx in range(1, len(legend)):
    nlcd_value[nlcd_value == legend[idx]] = idx

cmap = discrete_cmap()
fig, axs = plt.subplots()
plotPolygons(polygons_dict["polys"], axs, 'red')
mat = axs.pcolor(lon, lat, nlcd_value, cmap=cmap, vmin=1 - 0.5,
                      vmax=len(legend) - 0.5)
cax = plt.colorbar(mat, ticks=np.arange(1, len(legend)))
cax.ax.set_yticklabels(leg_str[1:])
plt.axis('off')
fig.tight_layout()
plt.show()



