# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 16:50:27 2021

@author: Tatu Leppämäki
"""

import json

def create_eupeg_json(df):
    """Transforms a Pandas dataframe to a EUPEG json"""
    filtered = df.reset_index()[['locations','loc_spans','coord_points']]
    
    all_toponyms = []
    for i in range(len(filtered)):
        row = filtered.iloc[i]
        json_entry = {'start':row['loc_spans'][0], 'end':row['loc_spans'][1], 'phrase':row['locations'],
                      'place':{'footprint':row['coord_points']}}
        all_toponyms.append(json_entry)
        
    eupeg_dict = {'toponyms':all_toponyms}
    
    return json.dumps(eupeg_dict, ensure_ascii=False)