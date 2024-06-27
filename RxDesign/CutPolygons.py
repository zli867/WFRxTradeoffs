import pickle
import os
from shapely.geometry import shape
import json
import matplotlib.pyplot as plt
from util import read_sensing_info, plotPolygons, plotLines
from shapely.ops import linemerge, unary_union, polygonize
import pickle

# NLCD
wf_filename = "/Volumes/Shield/WFRxTradeoffs/data/GRSM_MAIN_WF.json"
with open(wf_filename) as f:
    data = json.load(f)

polygon = shape(data["perimeter"])


def cut_polygon_by_line(polygon_bounds, lines):
    all_lines = lines.copy()
    all_lines.append(polygon_bounds)
    merged = linemerge(all_lines)
    borders = unary_union(merged)
    polygons = polygonize(borders)
    return list(polygons)

lines = []
line_dir = "/Volumes/Shield/WFRxTradeoffs/RxDesign/temp_lines/temp_lines"
filenames = os.listdir(line_dir)
for filename in filenames:
    print(filename)
    if ".pickle" in filename:
        cur_file = os.path.join(line_dir, filename)
        with open(cur_file, 'rb') as f:
            cur_line = pickle.load(f)
        lines.append(cur_line["line"])
        fig, ax = plt.subplots(figsize=(8, 6))
        plotPolygons([polygon], ax, 'black')
        plotLines([cur_line["line"]], ax, 'red')
        plt.show()

# split the polygon
cut_polygons = cut_polygon_by_line(polygon.boundary[0], lines)

for cut_polygon in cut_polygons:
    fig, ax = plt.subplots(figsize=(8, 6))
    plotPolygons([polygon], ax, 'black')
    plotLines(lines, ax, 'red')
    plotPolygons([cut_polygon], ax, 'yellow')
    plt.show()

# save temp polygons
filename = "/Volumes/Shield/WFRxTradeoffs/RxDesign/temp_polygons/polys_new.pickle"
res = {"polys": cut_polygons}
with open(filename, 'wb') as handle:
    pickle.dump(res, handle, protocol=pickle.HIGHEST_PROTOCOL)