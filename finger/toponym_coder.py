# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 18:53:37 2021

@author: Tatu Leppämäki
"""

#import pandas as pd
import requests
import aiohttp
import asyncio
from tqdm.asyncio import tqdm

#try:
#    from shapely.geometry import Point
#except (ImportError, FileNotFoundError) as e:
#    print("Unable to import Shapely. The geoparser works, but exporting to Shapely points is unavailable.")


class toponym_coder:
    
    def __init__(self, geocoder_url="http://vm5121.kaj.pouta.csc.fi:4000/v1/"):
        """
        Calls a geocoder at the defined URL and returns a dictionary of responses.
        """

        self.geocoder_url = geocoder_url
        assert self.geocoder_url, "A valid URL pointing to a running Pelias geocoding service must be provided."
        
        params = {'text':'Kamppi'}
        res = requests.get(geocoder_url+'search', params=params)
        assert res.status_code == 200, f"Geocoder from url {geocoder_url} did not return all OK. The path could be faulty or the service unavailable."

    async def geocode_toponyms(self, toponyms, columns=['coordinates', 'gid', 'layer', 'label', 'bbox'], params=None):
        """Input: a list of toponyms: in default operation, this is a lemmatized versions of the toponyms recognized in the previous step.
        TODO: EXPAND WITH COLUMNS AND PARAMS
        Outputs: 
        	UPDATE
            Lonlats - list of coordinates in WGS84 longitude-latitude format
            Labels - Textual descriptions of the toponym as returned by the geocoder
            GIDS - An unique label that internally identifies the location. These are not stable and can change as the data in the geocoder is updated."""

        lists = {key: list() for key in columns}

        responses = await self.batch_get(toponyms, params=params)

        for response in responses:
            # for each response, check if the returned something (if it failed, it will not have 'features'). NB! The status will still be 200 for empty responses
            if response and response['features']:

                for key in lists.keys():
                    # loop through the requested columns, append values
                    # because the keys may not be at the base level, I need to do this clumsy hardcode for acquiring the correct values

                    # related to geometry
                    if key in ('type', 'coordinates'):
                        lists[key].append(response['features'][0]['geometry'][key])
                    # if not, it's probably at the properties level
                    elif key != 'bbox':
                        lists[key].append(response['features'][0]['properties'][key])
                    # else a bounding box, which is at the base level
                    else:
                        lists[key].append(response['features'][0][key])
            else:
                # if nothing was returned, appends Nones to all lists
                for this_list in lists.values():
                    this_list.append(None)

        return lists

    async def batch_get(self, topos, params=None):
        """"This function forms the query urls, which are then asynchronoysly requested from the geocoder"""
        # avoid badgering the server with too many requests at once -> leads to http errors
        # this limits the concurrent connections to 15 (default 100)
        connector = aiohttp.TCPConnector(limit=15)

        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for topo in topos:
                if topo:
                    # if there's a lemmatized toponym, try searching with that. If not, return an empty string
                    url = f"{self.geocoder_url}search"
                    if params:
                    	url_params = {'text': topo, **params}
                    else:
                        url_params = {'text': topo}
                    task = asyncio.ensure_future(self.get_response(session, url, params=url_params))
                    tasks.append(task)
                else:
                    task = asyncio.ensure_future(self.return_none())
                    tasks.append(task)
            # tqdm.gather works as a wrapper for asyncio.gather: it adds a progress bar
            responses = await tqdm.gather(*tasks, desc="Geocoding...")

            return responses

    async def get_response(self, session, url, params=None):
        """Setup one request. If the response code is something other than 200, print the error code."""
        async with session.get(url, params=params) as response:
            if response.status != 200:
                print(url, response.status)
            return await response.json()
        
    async def return_none(self):
        return ""
"""
    def form_point(self, gn_result):
        if self.shp_points:
            return Point(float(gn_result.lng), float(gn_result.lat))
        else:
            return (gn_result.lng, gn_result.lat)
"""
