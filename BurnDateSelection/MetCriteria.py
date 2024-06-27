import numpy as np


def extract_PBL(x_idx, y_idx, metcro2d):
    pbl_series = metcro2d["PBL"][:, 0, x_idx, y_idx]
    return pbl_series


def extract_surface_WDSPD(x_idx, y_idx, metcro2d):
    wdspd_series = metcro2d["WSPD10"][:, 0, x_idx, y_idx]
    return wdspd_series


def extract_TEMP(x_idx, y_idx, metcro2d):
    temp_series = metcro2d["TEMP2"][:, 0, x_idx, y_idx]
    return temp_series


def extract_RH(x_idx, y_idx, metcro2d):
    # https://github.com/USEPA/CMAQ/blob/main/CCTM/src/emis/emis/SSEMIS.F
    AA = 610.94
    BB = 17.625
    CC = 243.04
    MWWAT = 18.0153
    MWAIR = 28.9628
    EPSWATER = MWWAT / MWAIR
    BLKTA = metcro2d["TEMP2"][:, 0:, x_idx, y_idx].flatten()
    BLKPRS = metcro2d["PRSFC"][:, 0, x_idx, y_idx].flatten()
    BLKQV = metcro2d["Q2"][:, 0, x_idx, y_idx].flatten()
    ESAT = AA * np.exp(BB * (BLKTA - 273.15) / (BLKTA - 273.15 + CC))
    BLKRH = BLKPRS * BLKQV / ((EPSWATER + BLKQV) * ESAT)
    BLKRH[BLKRH < 0.005] = 0.005
    BLKRH[BLKRH > 0.99] = 0.99
    RH = 100 * BLKRH
    return RH


def theta_U(u_wind):
    # https://wiki.openwfm.org/wiki/How_to_interpret_WRF_variables
    u_wind_theta = 0.5 * (u_wind[:, :, :-1, :-1] + u_wind[:, :, 1:, 1:])
    return u_wind_theta


def theta_V(v_wind):
    # https://wiki.openwfm.org/wiki/How_to_interpret_WRF_variables
    v_wind_theta = 0.5 * (v_wind[:, :, :-1, :-1] + v_wind[:, :, 1:, 1:])
    return v_wind_theta


def extract_transport_WDSPD(x_idx, y_idx, metcro2d, metcro3d, metdot3d):
    u_wind = theta_U(metdot3d["UWIND"][:])[:, :, x_idx, y_idx]
    v_wind = theta_V(metdot3d["VWIND"][:])[:, :, x_idx, y_idx]
    ZF = metcro3d["ZF"][:][:, :, x_idx, y_idx]
    PBL = metcro2d["PBL"][:][:, 0, x_idx, y_idx]
    t_step, layer_num = ZF.shape
    fraction = np.zeros(ZF.shape)
    for t in range(0, t_step):
        current_PBL = PBL[t]
        for lay in range(0, layer_num):
            current_layer_top = ZF[t, lay]
            current_layer_bottom = 0
            if lay > 0:
                current_layer_bottom = ZF[t, lay - 1]
            current_thickness = current_layer_top - current_layer_bottom
            if current_layer_top < current_PBL:
                fraction[t, lay] = current_thickness / current_PBL
            else:
                fraction[t, lay] = (current_PBL - current_layer_bottom) / current_PBL
                break
    wdspd = np.sqrt(u_wind ** 2 + v_wind ** 2)
    weighted_wdspd = np.sum(wdspd * fraction, axis=1)
    return weighted_wdspd


def extract_RAIN(x_idx, y_idx, metcro2d):
    RC = metcro2d["RC"][:][:, 0, x_idx, y_idx]
    RN = metcro2d["RN"][:][:, 0, x_idx, y_idx]
    rain_series = RC + RN
    return rain_series
