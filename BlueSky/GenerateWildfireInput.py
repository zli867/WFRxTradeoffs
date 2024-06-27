import BlueSkyInputGenerator
import pandas as pd
import json
from shapely.geometry import shape
import numpy as np
from datetime import datetime, timedelta

met_dir = "/home/zli867/NAM_12km/"
fire_file = "/Volumes/Shield/WFRxTradeoffs/data/GRSM_MAIN_WF.json"
fires = []
with open(fire_file) as json_file:
    fire_event = json.load(json_file)

fire_start_time = datetime.strptime(fire_event["start_UTC"], "%Y-%m-%d %H:%M:%S")
fire_end_time = datetime.strptime(fire_event["end_UTC"], "%Y-%m-%d %H:%M:%S")
fire = BlueSkyInputGenerator.generateBlueSkyFire(fire_event)
fire_start_time = datetime(fire_start_time.year, fire_start_time.month, fire_start_time.day)
fire_end_time = datetime(fire_end_time.year, fire_end_time.month, fire_end_time.day)

fires.append(fire)
met_data = BlueSkyInputGenerator.generateMetInfo(met_dir, fire_start_time, fire_end_time)
result = {"fires": fires, "met": met_data}
json_obj = json.dumps(result, indent=4)

# Generate BlueSKY input
input_filename = "/Volumes/Shield/WFRxTradeoffs/data/BlueSky/bsp_run/bsp_input/Smky_WF_Input.json"
with open(input_filename, 'w') as fout:
    print(json_obj, file=fout)
