import netCDF4 as nc
import pyproj
import numpy as np
from datetime import datetime
import fiona
from shapely.geometry import shape

def CMAQGrid2D(mcip_gridcro2d):
    """

    :param mcip_gridcro2d: CMAQ MCIP grid cros 2D output
    :return: a dictionary: {"crs": projection,
                            "X_ctr": x_center_grid,
                            "Y_ctr": y_center_grid,
                            "X_bdry": [x_min, x_max],
                            "Y_bdry": [y_min, y_max]}
    """
    ds = nc.Dataset(mcip_gridcro2d)
    lat_1 = ds.getncattr('P_ALP')
    lat_2 = ds.getncattr('P_BET')
    lat_0 = ds.getncattr('YCENT')
    lon_0 = ds.getncattr('XCENT')
    crs = pyproj.Proj("+proj=lcc +a=6370000.0 +b=6370000.0 +lat_1=" + str(lat_1)
                      + " +lat_2=" + str(lat_2) + " +lat_0=" + str(lat_0) +
                      " +lon_0=" + str(lon_0))
    xcell = ds.getncattr('XCELL')
    ycell = ds.getncattr('YCELL')
    xorig = ds.getncattr('XORIG')
    yorig = ds.getncattr('YORIG')

    ncols = ds.getncattr('NCOLS')
    nrows = ds.getncattr('NROWS')

    #> for X, Y cell centers
    x_center_range = np.linspace(xorig+xcell/2, (xorig+xcell/2)+xcell*(ncols-1), ncols)
    y_center_range = np.linspace(yorig+ycell/2, (yorig+ycell/2)+ycell*(nrows-1), nrows)

    Xcenters, Ycenters = np.meshgrid(x_center_range, y_center_range)

    #> for X, Y cell boundaries (i.e., cell corners)
    x_bound_range = np.linspace(xorig, xorig+xcell*ncols, ncols+1)
    y_bound_range = np.linspace(yorig, yorig+ycell*nrows, nrows+1)

    Xbounds, Ybounds = np.meshgrid(x_bound_range, y_bound_range)

    x_max = np.max(Xbounds)
    x_min = np.min(Xbounds)
    y_max = np.max(Ybounds)
    y_min = np.min(Ybounds)

    lon_ctr, lat_ctr = crs(Xcenters, Ycenters, inverse=True)

    time_data = ds['TFLAG'][:]
    cmaq_time_array = []
    for i in range(0, time_data.shape[0]):
        time_data_tmp = time_data[i, 0, :]
        time_str = str(time_data_tmp[0]) + str(time_data_tmp[1]).rjust(6, '0')
        parsed = datetime.strptime(time_str, '%Y%j%H%M%S')
        cmaq_time_array.append(parsed)

    res_dict = {"crs": crs, "X_ctr": Xcenters, "Y_ctr": Ycenters, "X_bdry": [x_min, x_max], "Y_bdry": [y_min, y_max],
                "Lat": lat_ctr, "Lon": lon_ctr, "X_uniq": x_center_range, "Y_uniq": y_center_range, "time": cmaq_time_array}
    return res_dict


def findSpatialIndex(loc_x, loc_y, X_ctr, Y_ctr):
    """
    :param loc_x: X of fire location in CMAQ projection
    :param loc_y: Y of fire location in CMAQ projection
    :param X_ctr: CMAQ grid X center
    :param Y_ctr: CMAQ grid Y center
    :return: x_idx, y_idx which are the fire location in CMAQ grid
    """
    dist = np.sqrt((X_ctr - loc_x) ** 2 + (Y_ctr - loc_y) ** 2)
    x_idx, y_idx = np.unravel_index(np.argmin(dist, axis=None), dist.shape)
    return x_idx, y_idx


def plotPolygons(polygon_list, ax, color):
    for current_polygon in polygon_list:
        if current_polygon.geom_type == "MultiPolygon":
            for geom in current_polygon.geoms:
                xs, ys = geom.exterior.xy
                ax.plot(xs, ys, color)
        else:
            xs, ys = current_polygon.exterior.xy
            ax.plot(xs, ys, color)


def plotLines(line_list, ax, color):
    for cur_lin in line_list:
        x, y = cur_lin.coords.xy
        ax.plot(x, y, color)


def get_crs(ds):
    projection = ds.GetProjection()
    crs = pyproj.Proj(projection)
    return crs


def read_sensing_info(ds):
    geotransform = ds.GetGeoTransform()
    nrows = ds.RasterYSize
    ncols = ds.RasterXSize
    x_corner_range = np.linspace(0, ncols - 1, ncols)
    y_corner_range = np.linspace(0, nrows - 1, nrows)
    x, y = np.meshgrid(x_corner_range, y_corner_range)
    X = geotransform[0] + x * geotransform[1] + y * geotransform[2]
    Y = geotransform[3] + x * geotransform[4] + y * geotransform[5]
    # shift to center
    X += geotransform[1] / 2
    Y += geotransform[4] / 2
    crs = get_crs(ds)
    info_dict = {
        "X": X,
        "Y": Y,
        "crs": crs
    }
    return info_dict


def StatePolygon(state_name_list):
    """
    List of States:
        Maryland, Iowa, Delaware, Ohio, Pennsylvania, Nebraska, Washington, Puerto Rico, Alabama,
        Arkansas, New Mexico, Texas, California, Kentucky, Georgia, Wisconsin, Oregon,
        Missouri, Virginia, Tennessee, Louisiana, New York, Michigan, Idaho, Florida,
        Alaska, Illinois, Montana, Minnesota, Indiana, Massachusetts, Kansas, Nevada,
        Vermont, Connecticut, New Jersey, District of Columbia, North Carolina, Utah,
        North Dakota, South Carolina, Mississippi, Colorado, South Dakota, Oklahoma,
        Wyoming, West Virginia, Maine, Hawaii, New Hampshire, Arizona, Rhode Island
    :param state_name: input the state name in the list
    :return: polygon of the state
    """
    us_shape_name = "/Volumes/Shield/HealthAnalysis/data/geo/US/cb_2018_us_state_20m.shp"
    us_states = fiona.open(us_shape_name)
    state_geo = []
    for state_name in state_name_list:
        for us_state in us_states:
            cur_name = us_state['properties']['NAME']
            if cur_name == state_name:
                state_geo.append(shape(us_state['geometry']))
    return state_geo


def FIPS_list(state_name_list):
    fips_list = []
    fips_dict = {'Alaska': '02', 'Alabama': '01', 'Arkansas': '05', 'Arizona': '04', 'California': '06', 'Colorado': '08',
                 'Connecticut': '09', 'District of Columbia': '11', 'Delaware': '10', 'Florida': '12', 'Georgia': '13',
                 'Hawaii': '15', 'Iowa': '19', 'Idaho': '16', 'Illinois': '17', 'Indiana': '18', 'Kansas': '20',
                 'Kentucky': '21', 'Louisiana': '22', 'Massachusetts': '25', 'Maryland': '24', 'Maine': '23',
                 'Michigan': '26', 'Minnesota': '27', 'Missouri': '29', 'Mississippi': '28', 'Montana': '30',
                 'North Carolina': '37', 'North Dakota': '38', 'Nebraska': '31', 'New Hampshire': '33',
                 'New Jersey': '34', 'New Mexico': '35', 'Nevada': '32', 'New York': '36', 'Ohio': '39',
                 'Oklahoma': '40', 'Oregon': '41', 'Pennsylvania': '42', 'Puerto Rico': '72', 'Rhode Island': '44',
                 'South Carolina': '45', 'South Dakota': '46', 'Tennessee': '47', 'Texas': '48', 'Utah': '49',
                 'Virginia': '51', 'Vermont': '50', 'Washington': '53', 'Wisconsin': '55', 'West Virginia': '54',
                 'Wyoming': '56'}
    for state_name in state_name_list:
        fips_list.append(fips_dict[state_name])
    return fips_list


def CountyPolygon(state_name_list):
    fips_list = FIPS_list(state_name_list)
    county_shape_name = "/Volumes/Shield/HealthAnalysis/data/geo/County/cb_2018_us_county_20m.shp"
    us_counties = fiona.open(county_shape_name)
    county_ids = []
    polygons = []
    for us_county in us_counties:
        state_fips = us_county['properties']["STATEFP"]
        county_fips = us_county['properties']["COUNTYFP"]
        county_id = state_fips + county_fips
        if state_fips in fips_list:
            county_ids.append(county_id)
            polygons.append(shape(us_county['geometry']))
    return county_ids, polygons