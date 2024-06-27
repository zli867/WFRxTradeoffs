import matplotlib.pyplot as plt
import numpy as np
import json
from shapely.geometry import shape, Polygon
from util import CMAQGrid2D
from datetime import datetime
import pandas as pd
from shapely.geometry import shape, mapping
import pickle

poly_filename = "/Volumes/Shield/WFRxTradeoffs/data/DesignedRx/updated_merged_poly_new.pickle"
cmaq_filename = "/Volumes/Shield/WFRxTradeoffs/data//METCRO2D_12US2_20130101"
cmaq_info = CMAQGrid2D(cmaq_filename)

with open(poly_filename, 'rb') as f:
    polygons_dict = pickle.load(f)

date_mapping = {
    0: datetime(2015, 12, 12),
    1: datetime(2015, 12, 11),
    2: datetime(2015, 12, 12),
    3: datetime(2016, 1, 14),
    4: datetime(2016, 2, 7),
    5: datetime(2015, 12, 10),
    6: datetime(2015, 12, 3),
    7: datetime(2015, 12, 4),
    8: datetime(2016, 2, 11),
    9: datetime(2016, 2, 14),
    10: datetime(2016, 2, 4),
    11: datetime(2016, 2, 27),
    12: datetime(2016, 2, 27),
    13: datetime(2016, 3, 27),
    14: datetime(2016, 3, 21),
    15: datetime(2016, 2, 5),
    16: datetime(2016, 1, 18),
    17: datetime(2016, 1, 17),
    18: datetime(2016, 2, 29),
    19: datetime(2016, 1, 29),
    20: datetime(2016, 3, 15)
}

polygon_info = {}
for i in range(0, len(polygons_dict["polys"])):
    polygon_info[i] = {
        "poly": polygons_dict["polys"][i]
    }

bsp_fire_info = []
# generate the information
fig, ax = plt.subplots(figsize=(8, 6))
for polygon_id in polygon_info.keys():
    polygon = polygon_info[polygon_id]["poly"]
    cur_burn_date = date_mapping[polygon_id]
    base_name = "Fire_" + datetime.strftime(cur_burn_date, "%Y%m%d")
    idx = 0
    cur_fire_info = {}
    if polygon.geom_type == "MultiPolygon":
        for geom in polygon.geoms:
            lons, lats = geom.exterior.xy
            ctr_lon, ctr_lat = list(geom.centroid.coords)[0]
            xs, ys = cmaq_info["crs"](lons, lats)
            current_polygon = Polygon(zip(xs, ys))
            area = current_polygon.area * 0.000247105 # acres
            sub_name = base_name + "_%d" % idx
            cur_fire_info = {
                "id": sub_name,
                "lat": ctr_lat,
                "lng": ctr_lon,
                "burned_area": area,
                "type": "rx",
                "perimeter": mapping(geom),
                "start_UTC": datetime(cur_burn_date.year, cur_burn_date.month, cur_burn_date.day, 15).strftime("%Y-%m-%d %H:%M:%S"),
                "end_UTC": datetime(cur_burn_date.year, cur_burn_date.month, cur_burn_date.day, 22).strftime("%Y-%m-%d %H:%M:%S")
            }
            idx += 1
    else:
        lons, lats = polygon.exterior.xy
        ctr_lon, ctr_lat = list(polygon.centroid.coords)[0]
        xs, ys = cmaq_info["crs"](lons, lats)
        current_polygon = Polygon(zip(xs, ys))
        area = current_polygon.area * 0.000247105
        cur_fire_info = {
            "id": base_name,
            "lat": ctr_lat,
            "lng": ctr_lon,
            "burned_area": area,
            "type": "rx",
            "perimeter": mapping(polygon),
            "start_UTC": datetime(cur_burn_date.year, cur_burn_date.month, cur_burn_date.day, 15).strftime("%Y-%m-%d %H:%M:%S"),
            "end_UTC": datetime(cur_burn_date.year, cur_burn_date.month, cur_burn_date.day, 22).strftime("%Y-%m-%d %H:%M:%S"),
        }
    bsp_fire_info.append(cur_fire_info)

with open('/Volumes/Shield/WFRxTradeoffs/data/New_designed_rx_fire_events.json', 'w') as f:
    json.dump(bsp_fire_info, f)