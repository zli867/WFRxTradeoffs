from util import CMAQGrid2D
from MetCriteria import extract_RH, extract_PBL, extract_RAIN, extract_TEMP, extract_surface_WDSPD, \
    extract_transport_WDSPD
from datetime import datetime, timedelta
import netCDF4 as nc
import numpy as np
import pandas as pd


filedir = "/storage/home/hcoda1/6/yh29/data4/HEI/outputs_2016/mcip"
# set row idx and col idx
x_idx = 102
y_idx = 301
select_hour = 18
start_time = datetime(2016, 1, 1)
end_time = datetime(2016, 1, 2)
current_time = start_time
reject_reason = []
reject_dates = []
select_dates = []
while current_time <= end_time:
    metcro2d_filename = "%s/METCRO2D_12US2_%s" %(filedir, current_time.strftime("%Y%m%d"))
    metcro3d_filename = "%s/METCRO3D_12US2_%s" % (filedir, current_time.strftime("%Y%m%d"))
    metdot3d_filename = "%s/METDOT3D_12US2_%s" % (filedir, current_time.strftime("%Y%m%d"))
    metcro2d_ds = nc.Dataset(metcro2d_filename)
    metcro3d_ds = nc.Dataset(metcro3d_filename)
    metdot3d_ds = nc.Dataset(metdot3d_filename)
    cmaq_info = CMAQGrid2D(metcro2d_filename)
    select_time = datetime(current_time.year, current_time.month, current_time.day, select_hour)
    time_idx = cmaq_info["time"].index(select_time)
    current_reason = ""
    is_selected = True
    # criteria 1: 24hr rain < 0.25 inch/day = 0.635cm
    utc_daily_total_rain = np.sum(extract_RAIN(x_idx, y_idx, metcro2d_ds))
    if utc_daily_total_rain >= 0.25:
        is_selected = False
        current_reason += "RAIN %.2f mm; " % utc_daily_total_rain
    # criteria 2: RH > 30%
    rh_series = extract_RH(x_idx, y_idx, metcro2d_ds)
    rh_value = rh_series[time_idx]
    if rh_value <= 30:
        is_selected = False
        current_reason += "RH value %.2f; " % rh_value
    # criteria 3: T < 85F = 302.594 K
    temp_series = extract_TEMP(x_idx, y_idx, metcro2d_ds)
    temp_value = temp_series[time_idx]
    if temp_value >= 302.594:
        is_selected = False
        current_reason += "Temp value %.2fK; " % temp_value
    # criteria 4: 503 m < PBL < 1981 m
    pbl_series = extract_PBL(x_idx, y_idx, metcro2d_ds)
    pbl_value = pbl_series[time_idx]
    if pbl_value <= 503 or pbl_value >= 1981:
        is_selected = False
        current_reason += "PBL value %.2fm; " % pbl_value
    # criteria 5: surface wind speed between 8 (3.57632m/s) and 14 mph (6.25856m/s)
    surface_wd_series = extract_surface_WDSPD(x_idx, y_idx, metcro2d_ds)
    surface_wd_value = surface_wd_series[time_idx]
    if surface_wd_value <= 3.57632 or surface_wd_value >= 6.25856:
        is_selected = False
        current_reason += "Surface WDSPD %.2f m/s; " % surface_wd_value
    # criteria 6: Transport wind between 9 and 20mph (4.02336-8.9408m/s)
    select_transport_wd_series = extract_transport_WDSPD(x_idx, y_idx, metcro2d_ds, metcro3d_ds, metdot3d_ds)
    select_transport_wd_value = select_transport_wd_series[time_idx]
    if select_transport_wd_value <= 4.02336 or select_transport_wd_value >= 8.9408:
        is_selected = False
        current_reason += "Transport WDSPD %.2f m/s" % select_transport_wd_value
    if is_selected:
        select_dates.append(current_time.strftime("%Y-%m-%d"))
    else:
        reject_dates.append(current_time.strftime("%Y-%m-%d"))
        reject_reason.append(current_reason)
    current_time = current_time + timedelta(days=1)

# save result
select_dict = {"Date": select_dates}
reject_dict = {"Date": reject_dates, "Reason": reject_reason}
select_df = pd.DataFrame(select_dict)
reject_df = pd.DataFrame(reject_dict)
select_df.to_csv('select_date.csv', index=False)
reject_df.to_csv('reject_date.csv', index=False)