import pickle
import matplotlib.pyplot as plt
import shapely.geometry as geom
from shapely.ops import unary_union
from util import plotPolygons

poly_filename = "/Volumes/Shield/WFRxTradeoffs/RxDesign/temp_polygons/polys_new.pickle"
with open(poly_filename, 'rb') as f:
    polygons_dict = pickle.load(f)

polygons = polygons_dict["polys"]
fig, ax = plt.subplots(figsize=(8, 6))
for i in range(0, len(polygons)):
    cur_polygon = polygons[i]
    xs, ys = cur_polygon.exterior.xy
    lng_ctr, lat_ctr = list(cur_polygon.centroid.coords)[0]
    ax.plot(xs, ys)
    ax.text(lng_ctr, lat_ctr, str(i), fontsize=8, ha='center', va='center')
ax.set_aspect('equal')

plt.axis('off')
plt.show()

# # # # #  merge index [11, 12, 13], [1, 6, 7, 8]
merged_polys = [[1, 6, 7, 8], [24, 25, 26, 39], [32, 33, 36, 37, 38], [12, 13, 14],
                [16, 17, 18], [34, 35], [19, 31, 30], [28, 29], [21, 22]]

merged_flags = []
merged_poly_set = set()
for i in range(0, len(merged_polys)):
    merged_flags.append(False)
    for j in range(0, len(merged_polys[i])):
        merged_poly_set.add(merged_polys[i][j])

poly_merged_res = []
for i in range(0, len(polygons)):
    if i in merged_poly_set:
        merged_idx = None
        merged_flag = None
        for j in range(0, len(merged_polys)):
            if i in merged_polys[j]:
                merged_idx = j
        poly_temp_list = merged_polys[merged_idx]
        merged_flag = merged_flags[merged_idx]
        if not merged_flag:
            cur_merge_poly = []
            for val in poly_temp_list:
                cur_merge_poly.append(polygons[val])
            new_poly = unary_union(cur_merge_poly)
            poly_merged_res.append(new_poly)
            merged_flags[merged_idx] = True
            print(poly_temp_list)
            print(new_poly.geom_type)
        else:
            continue
    else:
        poly_merged_res.append(polygons[i])

# save results
filename = "/Volumes/Shield/WFRxTradeoffs/RxDesign/temp_polygons/updated_merged_poly_new.pickle"
res = {"polys": poly_merged_res}
with open(filename, 'wb') as handle:
    pickle.dump(res, handle, protocol=pickle.HIGHEST_PROTOCOL)
