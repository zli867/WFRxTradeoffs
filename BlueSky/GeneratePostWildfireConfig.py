import json

wf_config_file = "/Volumes/Shield/WFRxTradeoffs/data/BlueSky/bsp_run/bsp_config/config_wf.json"
rx_consume_file = "/Volumes/Shield/WFRxTradeoffs/data/BlueSky/bsp_run/bsp_output/rx_region_fuel_consumption.json"
wf_consume_file = "/Volumes/Shield/WFRxTradeoffs/data/BlueSky/bsp_run/bsp_output/wildfire_region_fuel_consumption.json"

mapping_info = {
    "basal_accum_loading": ["ground fuels", "basal accumulations"],
    "duff_lower_loading": ["ground fuels", "duff lower"],
    "duff_upper_loading": ["ground fuels", "duff upper"],
    "ladderfuels_loading": ["canopy", "ladder fuels"],
    "lichen_loading": ["litter-lichen-moss", "lichen"],
    "litter_loading": ["litter-lichen-moss", "litter"],
    "midstory_loading": ["canopy", "midstory"],
    "moss_loading": ["litter-lichen-moss", "moss"],
    "nw_primary_loading": ["nonwoody", "primary live"],
    "nw_secondary_loading": ["nonwoody", "secondary live"],
    "overstory_loading": ["canopy", "overstory"],
    # "pile_clean_loading": [],
    # "pile_dirty_loading": [],
    # "pile_vdirty_loading": [],
    "shrubs_primary_loading": ["shrub", "primary live"],
    "shrubs_secondary_loading": ["shrub", "secondary live"],
    "snags_c1_foliage_loading": ["canopy", "snags class 1 foliage"],
    "snags_c1_wood_loading": ["canopy", "snags class 1 wood"],
    "snags_c1wo_foliage_loading": ["canopy", "snags class 1 no foliage"],
    "snags_c2_loading": ["canopy", "snags class 2"],
    "snags_c3_loading": ["canopy", "snags class 3"],
    "squirrel_midden_loading": ["ground fuels", "squirrel middens"],
    # "total_available_fuel_loading": [],
    "understory_loading": ["canopy", "understory"],
    # reference:
    # https://github.com/pnwairfire/bluesky/blob/1e29bc2450df688f1e00fa3a2ebb705963f0219a/bluesky/consumeutils.py#L203
    "w_rotten_3_9_loading": ["woody fuels", "1000-hr fuels rotten"],
    "w_rotten_9_20_loading": ["woody fuels", "10000-hr fuels rotten"],
    "w_rotten_gt20_loading": ["woody fuels", "10k+-hr fuels rotten"],
    "w_sound_0_quarter_loading": ["woody fuels", "1-hr fuels"],
    "w_sound_1_3_loading": ["woody fuels", "100-hr fuels"],
    "w_sound_3_9_loading": ["woody fuels", "1000-hr fuels sound"],
    "w_sound_9_20_loading": ["woody fuels", "10000-hr fuels sound"],
    "w_sound_gt20_loading": ["woody fuels", "10k+-hr fuels sound"],
    "w_sound_quarter_1_loading": ["woody fuels", "10-hr fuels"],
    "w_stump_lightered_loading": ["woody fuels", "stumps lightered"],
    "w_stump_rotten_loading": ["woody fuels", "stumps rotten"],
    "w_stump_sound_loading": ["woody fuels", "stumps sound"]
}

# start write code
with open(wf_config_file) as jsfile:
    wildfire_config = json.load(jsfile)

with open(rx_consume_file) as jsfile:
    rx_data = json.load(jsfile)

with open(wf_consume_file) as jsfile:
    wf_data = json.load(jsfile)

# extract wildfire fuelbed info
res_fuel_loadings = {}
fuel_burned_area = {}
wf_fire = wf_data["fires"][0]
wf_fuelbeds = wf_fire["activity"][0]["active_areas"][0]["perimeter"]["fuelbeds"]
wf_burned_area = wf_fire["activity"][0]["active_areas"][0]["perimeter"]["area"]
for i in range(0, len(wf_fuelbeds)):
    fuelbed = wf_fuelbeds[i]
    fuelbed_id = fuelbed["fccs_id"]
    res_fuel_loadings[fuelbed_id] = fuelbed["fuel_loadings"]
    res_fuel_loadings[fuelbed_id]["filename"] = "post_fuelbed_" + str(i)
    fuel_burned_area[fuelbed_id] = (fuelbed["pct"] / 100) * wf_burned_area

# TODO: Why there is a 110 fuelbeds, 75.72 acres
# TODO: consumption tons to tons/acre, what is the area of fuel? Is it burned_area * pct?
rx_fuel_loadings_mass = {}
# rx_fuel_loadings_mass = {"fccs_id": {mapping_info_keys: 0, ...}}
for fccs_id in res_fuel_loadings.keys():
    rx_fuel_loadings_mass[fccs_id] = {}
    for key in mapping_info.keys():
        rx_fuel_loadings_mass[fccs_id][key] = 0

# update rx fuel_loadings
rx_fires = rx_data["fires"]
for rx_fire in rx_fires:
    burned_area = rx_fire["activity"][0]["active_areas"][0]["perimeter"]["area"]
    fuelbeds = rx_fire["activity"][0]["active_areas"][0]["perimeter"]["fuelbeds"]
    for fuelbed in fuelbeds:
        fuelbed_pct = fuelbed["pct"] / 100
        fuelbed_id = fuelbed["fccs_id"]
        fuelbed_consumption = fuelbed["consumption"]
        rx_fuelbed_loadings = fuelbed["fuel_loadings"]
        fuelbed_area = burned_area * fuelbed_pct

        if fuelbed_id in rx_fuel_loadings_mass.keys():
            # add fuel loadings mass to rx_fuel_loadings_mass
            for rx_fuelbed in rx_fuelbed_loadings.keys():
                if rx_fuelbed in rx_fuel_loadings_mass[fuelbed_id].keys():
                    rx_fuel_loadings_mass[fuelbed_id][rx_fuelbed] += fuelbed_area * rx_fuelbed_loadings[rx_fuelbed]

            # remove fuelbed_consumption from rx_fuelbed_loadings
            for rx_fuelbed in rx_fuel_loadings_mass[fuelbed_id].keys():
                mapping_info_level_1 = mapping_info[rx_fuelbed][0]
                mapping_info_level_2 = mapping_info[rx_fuelbed][1]
                consumed_loading = fuelbed_consumption[mapping_info_level_1][mapping_info_level_2]["flaming"][0] + \
                                   fuelbed_consumption[mapping_info_level_1][mapping_info_level_2]["smoldering"][0] + \
                                   fuelbed_consumption[mapping_info_level_1][mapping_info_level_2]["residual"][0]
                rx_fuel_loadings_mass[fuelbed_id][rx_fuelbed] -= consumed_loading
        else:
            print(fuelbed_id + " area: %.2f" % fuelbed_area)

for fccs_id in res_fuel_loadings.keys():
    for fuelbed_type in rx_fuel_loadings_mass[fccs_id].keys():
        # update the fuel loadings in res_fuel_loadings
        res_fuel_loadings[fccs_id][fuelbed_type] = rx_fuel_loadings_mass[fccs_id][fuelbed_type] / fuel_burned_area[fccs_id]


# put the res_fuel_loadings to config file
wildfire_config["config"]["consumption"]["fuel_loadings"] = res_fuel_loadings
wildfire_config["config"]["consumption"]["consume_settings"]["all"]["canopy_consumption_pct"]["default"] = 20
# Generate Post wildfire config
output_filename = "/Volumes/Shield/WFRxTradeoffs/data/BlueSky/bsp_run/bsp_config/post_fire.json"
with open(output_filename, "w") as outfile:
    json.dump(wildfire_config, outfile)