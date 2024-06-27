from queue import Queue
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import shape
import json
from util import read_sensing_info, plotPolygons, plotLines
from osgeo import gdal
from shapely.geometry import LineString
from shapely.ops import linemerge, unary_union, polygonize
from scipy.ndimage import binary_dilation


def cut_polygon_by_line(polygon_bounds, line):
    merged = linemerge([polygon_bounds, line])
    borders = unary_union(merged)
    polygons = polygonize(borders)
    return list(polygons)


def generate_continue_region(start_x, start_y, values):
    frontier = Queue()
    mask_res = np.zeros(values.shape)
    frontier.put((start_x, start_y))
    m, n = values.shape
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, -1), (-1, -1), (-1, 1), (1, 1)]
    visited = {(start_x, start_y)}
    # search the start point
    while not frontier.empty():
        base_x, base_y = frontier.get()
        mask_res[base_x, base_y] = 1
        for cur_dir in dirs:
            dx, dy = cur_dir
            cur_x = base_x + dx
            cur_y = base_y + dy
            if 0 <= cur_x < m and 0 <= cur_y < n and values[cur_x, cur_y] == 1 and (cur_x, cur_y) not in visited:
                frontier.put((cur_x, cur_y))
                visited.add((cur_x, cur_y))
    return mask_res


def generate_split_line(start_x, start_y, end_x, end_y, lon, lat, line_mask):
    # post process the line mask
    # k = np.ones((3, 3), dtype=int)
    # line_mask = line_mask.astype(int)
    # line_mask = binary_dilation(line_mask == 0, k) & line_mask
    m, n = lon.shape
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, -1), (-1, -1), (-1, 1), (1, 1)]
    # start from the (start_x, start_y), find the path
    path_map = {}
    if end_x == start_x and end_y == start_y:
        return None
    else:
        find_path = False
        line_coords = []
        frontier = Queue()
        frontier.put((start_x, start_y))
        visited = {(start_x, start_y)}
        # search the start point
        while not frontier.empty():
            base_x, base_y = frontier.get()
            for cur_dir in dirs:
                dx, dy = cur_dir
                cur_x = base_x + dx
                cur_y = base_y + dy
                if 0 <= cur_x < m and 0 <= cur_y < n and line_mask[cur_x, cur_y] == 1 and (cur_x, cur_y) not in visited:
                    frontier.put((cur_x, cur_y))
                    visited.add((cur_x, cur_y))
                    path_map[(cur_x, cur_y)] = (base_x, base_y)
                    # get the path
                    if cur_x == end_x and cur_y == end_y:
                        this_node = (cur_x, cur_y)
                        while not (this_node[0] == start_x and this_node[1] == start_y):
                            line_coords.insert(0, (lon[this_node[0], this_node[1]], lat[this_node[0], this_node[1]]))
                            parent_node = path_map[this_node]
                            this_node = parent_node
                        line_coords.insert(0, (lon[start_x, start_y], lat[start_x, start_y]))
                        find_path = True
                        break
            if find_path:
                break
        if not find_path:
            print("Path Not Found")
            return None
    return LineString(line_coords)


def find_nearest_point(start_lon, start_lat, lon, lat, mask):
    distance = (lon - start_lon) ** 2 + (lat - start_lat) ** 2
    distance[mask != 1] = np.max(distance)
    x_idx, y_idx = np.unravel_index(np.argmin(distance, axis=None), distance.shape)
    return x_idx, y_idx


# # NLCD
# wf_filename = "/Users/zongrunli/Desktop/Wildfire_GA/data/GRSM_MAIN_WF.json"
# with open(wf_filename) as f:
#     data = json.load(f)
#
# polygon = shape(data["perimeter"])
#
# start_lon = -83.51134
# start_lat = 35.64775
# end_lon = -83.48976
# end_lat = 35.63868
# start_lon = -83.5268
# start_lat = 35.6624
# end_lon = -83.51283
# end_lat = 35.6490
# start_lon = -83.52959
# start_lat = 35.694918
# end_lon = -83.48648
# end_lat = 35.71997
# nlcd_file = "/Users/zongrunli/Desktop/Wildfire_GA/data/geo_static/NLCD_Clipped.tif"
# nlcd_ds = gdal.Open(nlcd_file, gdal.GA_ReadOnly)
# nlcd_value = nlcd_ds.ReadAsArray()
# nlcd_info = read_sensing_info(nlcd_ds)
# lon, lat = nlcd_info["crs"](nlcd_info["X"], nlcd_info["Y"], inverse=True)
# nlcd_value = nlcd_value.astype(float)
# # change nlcd_value to mask
# nlcd_value[(nlcd_value > 32) | (nlcd_value < 11)] = 0
# nlcd_value[(nlcd_value < 32) & (nlcd_value >= 11)] = 1
#
# # find the start and end point
# start_x_idx, start_y_idx = find_nearest_point(start_lon, start_lat, lon, lat, nlcd_value)
# end_x_idx, end_y_idx = find_nearest_point(end_lon, end_lat, lon, lat, nlcd_value)
# # start from start point and find a path
# line_mask = generate_continue_region(start_x_idx, start_y_idx, nlcd_value)
# fig, ax = plt.subplots(figsize=(8, 6))
# plt.pcolor(lon, lat, nlcd_value)
# plt.scatter([lon[start_x_idx, start_y_idx]], [lat[start_x_idx, start_y_idx]])
# plt.scatter([lon[end_x_idx, end_y_idx]], [lat[end_x_idx, end_y_idx]])
# plotPolygons([polygon], ax, 'black')
# plt.show()
#
# k = np.ones((3, 3), dtype=int)
# line_mask_test = line_mask.astype(int)
# line_mask_test = binary_dilation(line_mask_test == 0, k) & line_mask_test
# fig, ax = plt.subplots(figsize=(8, 6))
# plotPolygons([polygon], ax, 'black')
# plt.scatter([lon[start_x_idx, start_y_idx]], [lat[start_x_idx, start_y_idx]])
# plt.scatter([lon[end_x_idx, end_y_idx]], [lat[end_x_idx, end_y_idx]])
# plt.pcolor(lon, lat, line_mask_test)
# plt.show()
#
# line_res = generate_split_line(start_x_idx, start_y_idx, end_x_idx, end_y_idx, lon, lat, line_mask)
# # add head and tail
# line_x, line_y = line_res.coords.xy
# line_x.insert(0, start_lon)
# line_x.append(end_lon)
# line_y.insert(0, start_lat)
# line_y.append(end_lat)
# line_res = LineString(list(zip(line_x, line_y)))
#
# # visualize line
# fig, ax = plt.subplots(figsize=(8, 6))
# plotPolygons([polygon], ax, 'black')
# plotLines([line_res], ax, 'red')
# plt.show()
#
# # split the polygon
# cut_polygons = cut_polygon_by_line(polygon.boundary[0], line_res)
#
# for cut_polygon in cut_polygons:
#     fig, ax = plt.subplots(figsize=(8, 6))
#     plotPolygons([polygon], ax, 'black')
#     plotLines([line_res], ax, 'red')
#     plotPolygons([cut_polygon], ax, 'yellow')
#     plt.scatter([lon[start_x_idx, start_y_idx]], [lat[start_x_idx, start_y_idx]])
#     plt.scatter([lon[end_x_idx, end_y_idx]], [lat[end_x_idx, end_y_idx]])
#     plt.show()
# plotPolygons([polygon], ax, 'black')
# plt.scatter([x], [y])
#
# for cur_lin in [polygon.boundary[0]]:
#     x, y = cur_lin.coords.xy
#     ax.plot(x, y)
# plt.show()
# line_res = line_res.simplify(0.002, preserve_topology=False)
# plotLines([line_res], ax, 'blue')

# cut_polygons = cut_polygon_by_line(polygon.boundary[0], line_res)
# cut_polygons = [cut_polygons[1]]
# for current_polygon in cut_polygons:
#     if current_polygon.geom_type == "MultiPolygon":
#         for geom in current_polygon.geoms:
#             xs, ys = geom.exterior.xy
#             ax.plot(xs, ys)
#     else:
#         xs, ys = current_polygon.exterior.xy
#         ax.plot(xs, ys)
# plt.show()
# from shapely import wkt
# from shapely.ops import linemerge, unary_union, polygonize
#
# POLY = "POLYGON ((34.67491149902344 31.59900710035676, 34.85000610351562 31.59900710035676, 34.85000610351562 31.73867905688433, 34.67491149902344 31.73867905688433, 34.67491149902344 31.59900710035676))"
# LINE = "LINESTRING (34.64401245117188 31.63292168314889, 34.80812072753906 31.75911546882192)"
#
# poly = wkt.loads(POLY)
# line = wkt.loads(LINE)
#
# merged = linemerge([poly.boundary, line])
# borders = unary_union(merged)
# polygons = polygonize(borders)
# for p in polygons:
#     print(p)
#
# fig, ax = plt.subplots(figsize=(8, 6))
# plotPolygons([poly], ax, 'black')
# plotLines([line], ax, 'red')
# plt.show()