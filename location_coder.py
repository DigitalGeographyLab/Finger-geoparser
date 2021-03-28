# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 18:53:37 2021

@author: Tatu Leppämäki
"""
import geocoder.geonames as gn
#import pandas as pd
try:
    from shapely.geometry import Point
except ImportError:
    pass

class location_coder:
    
    def __init__(self, gn_username="", shp_points=False):
        """
        A geocoder, which currently accepts a Pandas dataframe (must be of certain
        format, which mostly makes this usable as part of a geoparser pipeline)
        and outputs a dataframe. The following columns are appended to the input df:
            
                1. gn_names: versions of the locations returned by querying GeoNames | List of strings or None
                2. gn_points: long/lat coordinate points in WGS84 | list of long/lat tuples or Shapely points
                
        TO RUN THIS GEOCODER, YOU CURRENTLY NEED A GEONAMES API KEY. The API key
        can be acquired simply by creating an account in https://www.geonames.org/
        Pass your account name as gn_username parameter.
        """
        self.shp_points = shp_points
        #if self.shp_points:
            #from shapely.geometry import Point
        self.username = gn_username
        assert self.username, "GeoNames API key (username) must be provided for the geocoder."
            
        test_result = gn("London", key=self.username)
        assert test_result.ok, "Geocoding failed. Did you enter a valid GeoNames API key?"
        
    def geocode_batch(self, locations, input_type="df"):
        """
        Applies geocoding to the lemmatized locations in the input dataframe.
        """
        locations['gn_names'] = None
        locations['gn_coord_points'] = None
        

        locations = locations.apply(self.geocode_set, axis=1)
        
        return locations
        
        
    def geocode_set(self, row):
        """
        Geocodes input Pandas series (rows).
        """
        
        # if locs present, continue. otherwise do nothing
        if row['locations_found']:
            loc_coord_points = []
            loc_names = []
            # 
            for loc in row['loc_lemmas']:
                #query geonames
                gn_result = gn(loc, key=self.username)
                # if succesful, add the name of the place in GN and coordinates
                if gn_result.ok:
                    loc_coord_points.append(self.form_point(gn_result))
                    loc_names.append(gn_result.address)
                else:
                    loc_coord_points.append(None)
                    loc_names.append(None)
                    
            if all(place==None for place in loc_names):
                loc_coord_points = None
                loc_names = None
                    
            row['gn_names'] = loc_names
            row['gn_coord_points'] = loc_coord_points
            
            return row
        else:
            return row
        
    def form_point(self, gn_result):
        if self.shp_points:
            return Point(float(gn_result.lng), float(gn_result.lat))
        else:
            return (gn_result.lng, gn_result.lat)