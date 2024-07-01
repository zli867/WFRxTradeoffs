# WFRxTradeoffs
## Code Description
This project mainly includes three modules for the research project. The three modules were implemented to:
* Select the dates that have favorable meteorological conditions for prescribed fires (BurnDateSelection folder).
* Design the prescribed fires based on the natural fire breaks (RxDesign folder).
* Generate the prescribed fire, wildfire, and post-burn wildfire inputs and configuration files (BlueSky folder).

## Burn Date Selection
1. MetCriteria.py: functions for extracting WRF meteorological variables.
2. DateSelection.py: reports the valid date for prescribed fires. For invalid dates, create the reasons.

## RxDesign
This module requires manual design of the fire breaks. Although the module provides functions to speed up the process, I did not figure out a method to do it automatically. The module provided here is useful for case studies but tedious for regional studies (such as the U.S. domain).

The process is discussed as follows:
1. Run ProduceBoundaryLine/ProduceBoundaryLineSlope.ipynb. The function is used to design each line of fire breaks. It creates the pickle file contains the shapely line object based on your design. The Jupyter Notebook provides interactive figures, and click the start point of the line you want to extract:
<p align="center">
  <img src="https://github.com/zli867/WFRxTradeoffs/blob/main/README_SRC/click_points.png"/>
</p>
After the process, it will provide the line which follows the terrain automatically:
<p align="center">
  <img src="https://github.com/zli867/WFRxTradeoffs/blob/main/README_SRC/created_line.png"/>
</p>
2. After finishing the first step, run CutPolygons.py. It uses the created line to intercept the fire boundary and returns multiple polygons.
3. Since the lines created in the first step sometimes are not smooth, there are small polygons that should be merged. The MergePolygons.py merges the small polygons to create the final designed Rx.
<p align="center">
  <img src="https://github.com/zli867/WFRxTradeoffs/blob/main/README_SRC/MergedPolys.png" width="50%"/>
</p>
4. You can do a burned area check and the fire break check before finalizing the Rx boundaries and putting it into BlueSky using PolygonAreaCheck.py and PolygonRegionCheck.py.

## BlueSky
### Data Format
A recommended fire object storage format:
Processed the reported prescribed burning information to json data.
```
{
  "fires": [
    {
      "id": fire_1_name,
      "date": "YYYY-MM-DD",
      "start_UTC": "YYYY-MM-DD HH:MM:SS"",
      "end_UTC": "YYYY-MM-DD HH:MM:SS",
      "lat": centroid_latitude_of_burned_region,
      "lng": centroid_longitude_of_burned_region,
      "burned_area": area_values,
      "type": burn_type,
      "perimeter": burn_area_polygon,
      "ignition_patterns": [
        {
          "ignition_time": [],
          "ignition_lat": [],
          "ignition_lng": []
        }
      ]
    },
    ...
    {
      "id": fire_n_name,
      "date": "YYYY-MM-DD",
      "start_UTC": "YYYY-MM-DD HH:MM:SS",
      "end_UTC": "YYYY-MM-DD HH:MM:SS",
      "lat": centroid_latitude_of_burned_region,
      "lng": centroid_longitude_of_burned_region,
      "burned_area": area_values,
      "type": burn_type,
      "perimeter": burn_area_polygon,
      "ignition_patterns": [
        {
          "ignition_time": [YYYY-MM-DD HH:MM:SS],
          "ignition_lat": [],
          "ignition_lng": []
        }
      ]
    }
  ]
}
```
### Processing Code
1. Wildfire: GenerateWildfireInput.py.
2. Prescribed Fire: create the fire JSON fire (GenerateNewDesignRxInfo.py). Then, use the JSON file to create BlueSky input (GenerateRxInput.py).
3. Post-burn Wildfire: create the configuration file and the file is used to update the fuel load after the prescribed fires (GeneratePostWildfireConfig.py). Then, create a JSON file for BlueSky input. Since the boundary and timing are the same as wildfire, use the GenerateWildfireInput.py.

## Authorship
The paper will be submitted to ES&T Air.
