# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 18:55:46 2021

@author: Tatu Leppämäki
"""


from finger.location_tagger import location_tagger
from finger.location_coder import location_coder
from finger.output_formatter import create_eupeg_json

import time

class geoparser:
    """
    The geoparser handles a whole geoparsing pipeline from geotagging to geocoding. 
    It accepts a list of Finnish text strings as input. It then runs those texts
    through a BERT-based neural linguistic and NER analysis pipeline built on Spacy.
    The objective of this analysis is to find references to locations, such as
    countries, towns, remarkable places etc., although the pipeline also runs general
    named entity recognition and things like dependency parsing and part-of-speech tagging
    on the side. Each input sentence can have zero to n locations in them. The locations are
    lemmatized using the Voikko library. The first part of the geoparsing process is called (geo)tagging.
    
    The tagger results are gathered on a Pandas dataframe consisting of five columns,
    with each analysis of a sentence on a single row. The dataframe is passed to
    the (geo)coder, which attempts to return coordinate representations of the locations.
    Currently, it relies on the GeoNames gazetteer, which is queried using a Python
    module called GeoCoder. If locations are found, coordinate point representations
    of them are returned as tuples or as Shapely points in WGS84 (EPSG:4326) CRS.

    """
    
    def __init__(self, pipeline_path="fi_geoparser", use_gpu=False, 
                 output_df=True, gn_username="", verbose=True):
        """
        Parameters:
        pipeline_path | String: name of the Spacy pipeline, which is called with spacy.load().
                                "fi_geoparser", which is the installation name, by default,
                                however, a path to the files can also be provided.
                                
        
        use_gpu | Boolean: Whether the pipeline is run on the GPU (significantly faster, but often missing in
                           e.g. laptops) or CPU (slower but should run every time). Default True.
                           
        output_df | Boolean: If True, the output will be a Pandas DataFrame. False does nothing currently.
        
        gn_username | String: GeoNames API key, or username, which is used for geocoding.
                              Mandatory, get from https://www.geonames.org/
        
        verbose | Boolean: Prints progress reports. Default True.
        

        """

        self.tagger = location_tagger(pipeline_path, use_gpu=use_gpu)
        
        self.coder = location_coder(gn_username=gn_username)
        
        self.verbose=verbose
        
        
    def geoparse(self, texts, ids=None, explode_df=False, return_shapely_points=False,
                  drop_non_locations=False, output='all', filter_toponyms=True, entity_tags=['LOC']):
        """
        The whole geoparsing pipeline.
        
        Input:
            texts | A string or a list of input strings: The input text(s)
            *ids | String, int, float or a list: Identifying element of each input, e.g. tweet id. Must be 
                  the same length as texts
            *explode_df | Boolean: Whether to have each location "hit" on separate rows in the output. Default False
            *return_shapely_points | Boolean: Whether the coordinate points of the locations are 
                                         regular tuples or Shapely points. Default False.
            *drop_non_locations | Boolean: Whether the sentences where no locations were found are
                                        included in the output. Default False (non-locs are included).
            *output | String: What's included in the output and in what format it is.
                                        Possible values: 
                                            1. 'all': All columns listed below as a dataframe
                                            TODO 2. 'essential': Dataframe trimmed down selection of columns
                                            3. 'eupeg': 
            *filter_toponyms | Boolean: Whether to filter out almost certain false positive toponyms.
                                        Currently removes toponyms with length less than 2. Default True.
            
        Output columns:
            Pandas Dataframe containing columns:
                1. input_text: the input sentence | String
                2. doc: Spacy doc object of the sent analysis. See https://spacy.io/api/doc | Doc
                3. locations_found: Whether locations were found in the input sent | Bool
                4. locations: locations in the input text, if found | list of strings or None
                5. loc_lemmas: lemmatized versions of the locations | list of strings or None
                6. loc_spans: the index of the start and end characters of the identified 
                              locations in the input text string | tuple
                7. input_order: the index of the inserted texts. i.e. the first text is 0, the second 1 etc.
                                Makes it easier to reassemble the results if they're exploded | int'
                8. names: versions of the names returned by querying GeoNames | List of strins or None
                9. coord_points: long/lat coordinate points in WGS84 | list of long/lat tuples or Shapely points
                10.*id: The identifying element tied to each input text, if provided | string, int, float
            OR
            EUPEG (see here: https://github.com/geoai-lab/EUPEG) style json dump, with restucturing data and renaming headers to be in line. 
            Mostly meant for evaluation purposes. This option only allows one text to be processed at once (no batch processing).
            
        """
        assert texts, "Input missing. Expecting a (list of) strings."
        
        # fix if someone passes just a string
        if isinstance(texts, str):
            texts = [texts]
            
        if output.lower() == 'eupeg':
            explode_df = True
        
        # check that ids are in proper formats and lengths
        if ids:
            if isinstance(ids, (str, int, float)):
                ids = [ids]
            assert len(texts) == len(ids), "If ids are passed, the number of ids and texts must be equal."
            
        
        if self.verbose:
            print("Starting geotagging...")
        t = time.time()
        
        # TOPONYM RECOGNITION
        tag_results = self.tagger.tag_sentences(texts, ids, explode_df=explode_df,
                                                drop_non_locs=drop_non_locations,
                                                filter_toponyms=filter_toponyms,
                                                entity_tags=entity_tags)

        if self.verbose:
            successfuls = tag_results['locations_found'].tolist()
            print("Finished geotagging after", round(time.time()-t, 2),"s.", successfuls.count(True), "location hits found.")
            print("Starting geocoding...")
        
        # TOPONYM RESOLVING
        geocode_results = self.coder.geocode_batch(tag_results, shp_points=False,
                                                   exploded=explode_df)
        
        
        if self.verbose:    
            print("Finished geocoding, returning output.")
            print("Total elapsed time:", round(time.time()-t, 2),"s")
            
        if output.lower() == 'eupeg':
            return create_eupeg_json(geocode_results)
        else:
            return geocode_results
