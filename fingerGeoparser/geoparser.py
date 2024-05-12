# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 18:55:46 2021

@author: Tatu Leppämäki

"""


from fingerGeoparser.toponym_tagger import toponym_tagger
from fingerGeoparser.toponym_coder import toponym_coder
from fingerGeoparser.output_formatter import create_eupeg_json


import time, asyncio, pandas as pd

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
    
    def __init__(self,
             pipeline_path="fi_geoparser",
             use_gpu=False,
             output_df=True,
             verbose=True,
             geocoder_url="http://vm5121.kaj.pouta.csc.fi:4000/v1/"):
        """
        Parameters:
        pipeline_path | String: name of the Spacy pipeline, which is called with spacy.load().
                                "fi_geoparser", which is the installation name, by default,
                                however, a path to the files can also be provided.
                                
        
        use_gpu | Boolean: Whether the pipeline is run on the GPU (significantly faster, but often missing in
                           e.g. laptops) or CPU (slower but should run every time). Default True.
                           
        output_df | Boolean: If True, the output will be a Pandas DataFrame. False does nothing currently.
        
        verbose | Boolean: Prints progress reports. Default True.
        
        geocoder_url : str, optional
            URL for the Pelias geocoder instance. Default instance is maintained by the author for now and is located at "http://vm5121.kaj.pouta.csc.fi:4000/v1/".

        """

        self.tagger = toponym_tagger(pipeline_path, use_gpu=use_gpu)
        
        self.coder = toponym_coder(geocoder_url)
        
        self.verbose=verbose
        
        
    def geoparse(self, 
             texts, 
             ids=None, 
             explode_df=True, 
             return_shapely_points=False, 
             preprocess_texts=False,
             drop_non_locations=False, 
             output='all', 
             filter_toponyms=True, 
             entity_tags=['LOC', 'FAC', 'GPE'],
             geocoder_columns =['coordinates', 'gid', 'layer', 'label', 'bbox'],
             geocoder_params = None):
        """
        The whole geoparsing pipeline.

        Input:
            texts | str or List[str]: A string or a list of input strings representing the text(s) to be processed.
            
            ids | str, int, float, or List[str/int/float], optional: Identifying element of each input, e.g., tweet id. 
                  Must be the same length as texts. Default is None.
                  
            explode_df | bool, optional: Whether to have each location "hit" on separate rows in the output. Default is True.
            
            return_shapely_points | bool, optional: Whether the coordinate points of the locations are regular tuples 
                                                or Shapely points. Default is False.
                                                
            preprocess_texts | bool, optional: Whether to preprocess the input texts before geoparsing. Default is False.
            
            drop_non_locations | bool, optional: Whether the sentences where no locations were found are included in the output. 
                                                Default is False (non-locs are included).
                                                
            output | str, optional: What's included in the output and in what format it is. Possible values: 
                                    'all': All columns listed below as a dataframe
                                    'eupeg': EUPEG style JSON dump. Default is 'all'.
                                    
            filter_toponyms | bool, optional: Whether to filter out almost certain false positive toponyms. 
                                               Currently removes toponyms with a length less than 2. Default is True.
                                               
            entity_tags | List[str], optional: Which named entity tags to count as toponyms. Default is ['LOC', 'FAC', 'GPE'].
            
            geocoder_columns | List[str], optional: Columns to include in the geocoder results. Default is 
                                                     ['coordinates', 'gid', 'layer', 'label', 'bbox'].
            geocoder_params | Dict[str], optional: Parameters to limit the search to, for example, a certain country. Provide as {'parameter':'value'} dictionaries. For example: {'boundary.country':'FIN'} See https://github.com/pelias/documentation/blob/master/search.md for a full list of search parameters.

        Output:
            Pandas DataFrame containing columns:
                - input_text: the input sentence
                - doc: Spacy doc object of the sent analysis.
                - locations_found: Whether locations were found in the input sent.
                - locations: locations in the input text, if found.
                - loc_lemmas: lemmatized versions of the locations.
                - loc_spans: the index of the start and end characters of the identified locations 
                              in the input text string.
                - input_order: the index of the inserted texts. i.e., the first text is 0, the second 1, etc.
                               Makes it easier to reassemble the results if they're exploded.
                - names: versions of the names returned by querying GeoNames.
                - coord_points: long/lat coordinate points in WGS84.

        Returns:
            Pandas DataFrame or dict: Depending on the 'output' parameter, either a Pandas DataFrame is returned 
                                       containing the geoparsing results, or a dictionary in EUPEG style JSON format.
        """

        # Validate inputs
        if not texts:
            raise ValueError("Input texts are missing. Expecting a string or a list of strings.")

        # fix if someone passes just a string
        if isinstance(texts, str):
            texts = [texts]
            
        if output.lower() == 'eupeg':
            explode_df = True
        
        # check that ids are in proper formats and lengths
        if ids:
            if isinstance(ids, (str, int, float)):
                ids = [ids]
            if len(ids) != len(texts):
                raise ValueError("If ids are provided, the number of ids must be equal to the number of texts.")
            
        
        if self.verbose:
            print("Starting geotagging...")
        t = time.time()
        
        # TOPONYM RECOGNITION
        tag_results = self.tagger.tag_sentences(texts, ids, explode_df=explode_df,
                                                drop_non_locs=drop_non_locations,
                                                filter_toponyms=filter_toponyms,
                                                entity_tags=entity_tags,
                                               preprocess=preprocess_texts)

        if self.verbose:
            successfuls = tag_results['toponyms_found'].tolist()
            print("Finished geotagging after", round(time.time()-t, 2),"s.", successfuls.count(True), "location hits found.")
            print("Starting geocoding...")
        
        # TOPONYM RESOLVING
        # TODO: Reimplement shp_points
        geocode_results = asyncio.run(self.coder.geocode_toponyms(tag_results['topo_lemmas'].tolist(),
                                                   columns=geocoder_columns))

        
        geocoded =  pd.DataFrame(geocode_results)
        
        tag_results = tag_results.reset_index(drop=True)
        
        # concatenate (add the columns) from the geocoder results to the tagging results to produce the final result
        results = pd.concat([tag_results, geocoded], axis=1)
        
        if self.verbose:
            print("Finished geocoding, returning output.")
            print("Total elapsed time:", round(time.time()-t, 2),"s")
            
        if output.lower() == 'eupeg':
            return create_eupeg_json(results)
        else:
            return results

