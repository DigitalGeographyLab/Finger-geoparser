# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 18:51:53 2021

@author: Tatu Leppämäki
"""


import spacy 


class location_tagger:
    """
    This class initiates a Finnish NER tagger using Spacy.
    
    A NER tagger object can be used to tag location mentions in input texts. It accepts list of strings
    as input and outputs a Pandas dataframe, which is then passed on to the geocoder.
    
    Parameters:
        pipeline_path | String: name of the Spacy pipeline, which is called with spacy.load().
                                "fi_geoparser", which is the installation name, by default,
                                however, a path to the files can also be provided.
    
        
        use_gpu | Boolean: Whether the pipeline is run on the GPU (significantly faster, but often missing in
                           e.g. laptops) or CPU (slower but should run every time)
                           
        output_df | Boolean: If True, the output will be a Pandas DataFrame. If False, a dictionary.
                            Currently, False does nothing. Left in if newer versions implement something
                            other than Pandas (just nested dictionaries?)
        """
    
        
    def __init__(self, pipeline_path="fi_geoparser", use_gpu=True, 
                 output_df=True):
        if use_gpu:
            spacy.require_gpu()
        else:
            spacy.require_cpu()
        
        self.output_df = output_df
        
        self.ner_pipeline = spacy.load(pipeline_path)
        

        

        
    def tag_sentences(self, input_texts, ids, explode_df=False, drop_non_locs=False,
                            filter_toponyms = True, entity_tags=['LOC']
        ):
        """Input:            
            texts | A string or a list of input strings: The input 
            *ids | String, int, float or a list: Identifying element of each input, e.g. tweet id. Must be 
                  the same length as texts
            *explode_df | Boolean: Whether to have each location "hit" on separate rows in the output. Default False
            *drop_non_locations | Boolean: Whether the sentences where no locations were found are
                                        included in the output. Default False (locs are included).
            *filter_toponyms | Boolean: Whether to filter out almost certain false positive toponyms.
                                        Currently removes toponyms with length less than 2. Default True.
        
        Output: Pandas DF containing columns:
                1. input_text: the input sentence | String
                2. doc: Spacy doc object of the sent analysis. See https://spacy.io/api/doc | Doc
                3. locations_found: Whether locations were found in the input sent | Bool
                4. locations: locations in the input text, if found | list of strings or None
                5. loc_lemmas: lemmatized versions of the locations | list of strings or None
                6. loc_spans: the index of the start and end characters of the identified 
                              locations in the input text string | tuple
                7. input_order: the index of the inserted texts. i.e. the first text is 0, the second 1 etc.
                                Makes it easier to reassemble the results if they're exploded | int'
                *8. id: The identifying element tied to each input text, if provided | string, int, float 
        """
        assert input_texts, "No input provided. Make sure to input a list of strings."
        tagged_sentences = []
        
        self.explode_df = explode_df
        
        self.drop_non_locs = drop_non_locs
        
        self.filter_toponyms = filter_toponyms
        
        self.entity_tags = entity_tags
        
        # loop input sentences, gather the tagged dictionary results to a list
        for sent in input_texts:
            tag_results = self.tag_sentence(sent)
            tagged_sentences.append(tag_results)
        
        return self.to_dataframe(tagged_sentences, ids)
        """
        if self.output_df:
            return self.to_dataframe(tagged_sentences)
        else:
            return tagged_sentences
        """
            
    def tag_sentence(self, sent):
        """Input: a sentence to tag (string)
        Output: a dictionary with the same variables as listed in 'tag_sentences'"""
        doc = self.ner_pipeline(sent)
        
        # if the tagger created an output, i.e. at least one of the words in the input
        # was tagged, create an output of that. Otherwise, return a mostly empty dict
        docs = []
        locs = []
        loc_lemmas = []
        loc_spans = []
        locations_found = False

        if doc:
            # gather the NER labels found to a list 
            labels = [ent.label_ for ent in doc.ents]

            locs = []
            # looping through the entities, collecting required information
            # namely, the raw toponym text, its lemmatized form and the span as tuple
            for ent in doc.ents:
                if ent.label_ in self.entity_tags:
                    # apply filtering if requested
                    if self.filter_toponyms:
                        # length filtering 
                        if len(ent.text)>1:
                            locs.append(ent.text)
                            loc_lemmas.append(ent.lemma_.replace("#",""))
                            loc_spans.append((ent.start_char, ent.end_char))
                            locations_found = True
                    else:
                        locs.append(ent.text)
                        loc_lemmas.append(ent.lemma_.replace("#",""))
                        loc_spans.append((ent.start_char, ent.end_char))
                        locations_found = True
            docs.append(doc)

        if locations_found:        
            sent_results = {'input_text': sent, 'doc': doc, 'locations_found': locations_found, 
                            'locations': locs, 'loc_lemmas': loc_lemmas, 'loc_spans': loc_spans}
        else:
            sent_results = {'input_text': sent, 'doc': doc, 'locations': None, 'loc_lemmas': None,
                    'loc_spans': None, 'locations_found': locations_found}

        return sent_results
        
    def to_dataframe(self, results, ids):
        import pandas as pd

        df = pd.DataFrame(results)
        
        
        if ids:
            df['id'] = ids
            
        df['input_order'] = df.index
        
        # split the possible list contents into multiple rows
        if self.explode_df:
            df = df.apply(lambda x: x.explode() if x.name in ['locations', 'loc_lemmas', 'loc_spans'] else x)
        if self.drop_non_locs:
            return self.drop_non_locations(df)
        else:
            return df
    
    def drop_non_locations(self, df):
        df = df[df['locations_found']]
        return df