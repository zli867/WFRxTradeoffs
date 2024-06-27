from datetime import datetime, timedelta
import numpy as np
import fiona
from shapely.geometry import shape, Point


def convertPolygonToList(polygon_object):
    polygon_coordinates = list(polygon_object.exterior.coords)
    polygon_2d_list = [[coord[0], coord[1]] for coord in polygon_coordinates]
    return polygon_2d_list


def generateBlueSkyFire(fire_event):
    lng_ctr, lat_ctr = fire_event["lng"], fire_event["lat"]
    fire_polygon = shape(fire_event["perimeter"])
    ploygon_boundary = convertPolygonToList(fire_polygon)
    utc_start_time = datetime.strptime(fire_event["start_UTC"], "%Y-%m-%d %H:%M:%S")
    utc_end_time = datetime.strptime(fire_event["end_UTC"], "%Y-%m-%d %H:%M:%S")
    # calculate utc
    utc_offset = utc_zone(lng_ctr, lat_ctr)
    # fire start time, end time
    negative = False
    if utc_offset[0] == "-":
        delta = datetime.strptime(utc_offset[1:], "%H:%M") - datetime.strptime("00:00", "%H:%M")
        negative = True
    else:
        delta = datetime.strptime(utc_offset, "%H:%M") - datetime.strptime("00:00", "%H:%M")

    if negative:
        ignition_start_local_time = utc_start_time - delta
        ignition_end_local_time = utc_end_time - delta
    else:
        ignition_start_local_time = utc_start_time + delta
        ignition_end_local_time = utc_end_time + delta
    start_local_time = datetime(ignition_start_local_time.year, ignition_start_local_time.month, ignition_start_local_time.day)
    end_local_time = datetime(ignition_end_local_time.year, ignition_end_local_time.month, ignition_end_local_time.day) + timedelta(days=1)
    fire_dict = {"id": fire_event["id"],
                 "type": fire_event["type"],
                 "fuel_type": "natural",
                 "activity": [
                     {
                         "active_areas": [
                             {
                                 "utc_offset": utc_offset,
                                 "start": datetime.strftime(start_local_time, "%Y-%m-%dT%H:%M:%S"),
                                 "end": datetime.strftime(end_local_time, "%Y-%m-%dT%H:%M:%S"),
                                 "ignition_start": datetime.strftime(ignition_start_local_time, "%Y-%m-%dT%H:%M:%S"),
                                 "ignition_end": datetime.strftime(ignition_end_local_time, "%Y-%m-%dT%H:%M:%S"),
                                 "country": "USA",
                                 "ecoregion": "southern",
                                 "perimeter": {
                                     "polygon": ploygon_boundary
                                 }
                             }
                         ]
                     }
                 ]}
    return fire_dict


def generateMetInfo(met_dir, start_time, end_time):
    files = []
    current_date = start_time
    while current_date <= end_time:
        filename = met_dir + str(current_date.year) + "/" + datetime.strftime(current_date, "%Y%m%d") + "_nam12"
        file = {"file": filename,
                "first_hour": datetime.strftime(current_date, "%Y-%m-%d") + "T00:00:00",
                "last_hour": datetime.strftime(current_date, "%Y-%m-%d") + "T23:00:00"}
        files.append(file)
        current_date = current_date + timedelta(days=1)
    res_dict = {"files": files}
    return res_dict


def utc_zone(lon, lat):
    utc_file = "/Users/zongrunli/Desktop/Wildfire_GA/data/TimeZone/timezone.shp"
    utc_zones = fiona.open(utc_file)
    fire_point = Point(lon, lat)
    zone_value_res = None
    for utc_zone in utc_zones:
        zone_value = utc_zone['properties']['ZONE']
        zone_geo = shape(utc_zone['geometry'])
        if zone_geo.contains(fire_point):
            zone_value_res = zone_value
            break
    # convert zone value to str
    if zone_value_res < 0:
        zone_value_res_pos = -zone_value_res
        hour_num = int(zone_value_res_pos)
        minute_num = int((zone_value_res_pos - hour_num) * 60)
        res = "-" + str(hour_num).rjust(2, '0') + ":" + str(minute_num).rjust(2, '0')
    else:
        hour_num = int(zone_value_res)
        minute_num = int((zone_value_res - hour_num) * 60)
        res = "+" + str(hour_num).rjust(2, '0') + ":" + str(minute_num).rjust(2, '0')
    return res