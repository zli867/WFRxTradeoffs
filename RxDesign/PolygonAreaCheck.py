import matplotlib.pyplot as plt
import numpy as np
import json
from shapely.geometry import shape, Polygon
from util import CMAQGrid2D
from datetime import datetime
import pandas as pd
from shapely.geometry import shape, mapping
import pickle


poly_filename = "/Volumes/Shield/WFRxTradeoffs/RxDesign/temp_polygons/updated_merged_poly_new.pickle"
cmaq_filename = "/Users/zongrunli/Desktop/Wildfire_GA/data/METCRO2D_12US2_20130101"
cmaq_info = CMAQGrid2D(cmaq_filename)

with open(poly_filename, 'rb') as f:
    polygons_dict = pickle.load(f)

fig, ax = plt.subplots(figsize=(8, 6))

polygons = polygons_dict["polys"]
for polygon in polygons:
    if polygon.geom_type == "MultiPolygon":
        for geom in polygon.geoms:
            lons, lats = geom.exterior.xy
            xs, ys = cmaq_info["crs"](lons, lats)
            current_polygon = Polygon(zip(xs, ys))
            ctr_x, ctr_y = list(current_polygon.centroid.coords)[0]
            area = current_polygon.area * 0.000247105
            plt.plot(xs, ys)
            ax.text(ctr_x, ctr_y, "%.2f" % area, fontsize=8, ha='center', va='center')
    else:
        lons, lats = polygon.exterior.xy
        xs, ys = cmaq_info["crs"](lons, lats)
        current_polygon = Polygon(zip(xs, ys))
        ctr_x, ctr_y = list(current_polygon.centroid.coords)[0]
        area = current_polygon.area * 0.000247105
        plt.plot(xs, ys)
        ax.text(ctr_x, ctr_y, "%.2f" % area, fontsize=8, ha='center', va='center')

ax.set_aspect('equal')
plt.axis('off')
plt.show()