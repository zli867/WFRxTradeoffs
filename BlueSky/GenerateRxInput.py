import BlueSkyInputGenerator
import pandas as pd
import json
from shapely.geometry import shape
import numpy as np
from datetime import datetime, timedelta

met_dir = "/home/zli867/NAM_12km/"
fire_file = "/Volumes/Shield/WFRxTradeoffs/data/DesignedRx/New_designed_rx_fire_events.json"
fires = []
with open(fire_file) as json_file:
    fire_events = json.load(json_file)

fire_time_range = []
for fire_event in fire_events:
    fire_time_range.append(datetime.strptime(fire_event["start_UTC"], "%Y-%m-%d %H:%M:%S"))
    fire_time_range.append(datetime.strptime(fire_event["end_UTC"], "%Y-%m-%d %H:%M:%S"))
    current_fire = BlueSkyInputGenerator.generateBlueSkyFire(fire_event)
    fires.append(current_fire)

fire_start_time = min(fire_time_range) - timedelta(days=1)
fire_end_time = max(fire_time_range) + timedelta(days=1)
fire_start_time = datetime(fire_start_time.year, fire_start_time.month, fire_start_time.day)
fire_end_time = datetime(fire_end_time.year, fire_end_time.month, fire_end_time.day)
met_data = BlueSkyInputGenerator.generateMetInfo(met_dir, fire_start_time, fire_end_time)

result = {"fires": fires, "met": met_data}
json_obj = json.dumps(result, indent=4)

# Generate BlueSKY input
input_filename = "/Volumes/Shield/WFRxTradeoffs/data/BlueSky/bsp_run/bsp_input/Smky_Rx_Input_New.json"
with open(input_filename, 'w') as fout:
    print(json_obj, file=fout)