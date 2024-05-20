# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 18:51:53 2021

@author: Tatu Leppämäki
"""


import spacy, pandas as pd, re

from tqdm import tqdm


class toponym_tagger:
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
            resp = spacy.prefer_gpu()
            
            if use_gpu and not resp:
                print("Using GPU failed, falling back on CPU...")
        
        self.output_df = output_df
        
        self.ner_pipeline = spacy.load(pipeline_path)
        
    def tag_sentences(self, input_texts, ids, explode_df=False, drop_non_locs=False, preprocess=False,
                            filter_toponyms = True, entity_tags=['LOC', 'FAC', 'GPE']
        ):
        """Input:            
            texts | A string or a list of input strings: The input 
            *ids | String, int, float or a list: Identifying element of each input, e.g. tweet id. Must be 
                  the same length as texts
            *explode_df | Boolean: Whether to have each location "hit" on separate rows in the output. Default False
            *drop_non_locations | Boolean: Whether the sentences where no locations were found are
                                        included in the output. Default False.
            *preprocess | Boolean: Whether to remove noise from the input texts, such as @-mentions and urls.
            *filter_toponyms | Boolean: Whether to filter out almost certain false positive toponyms.
                                        Currently removes toponyms with length less than 2. Default True.
        
        Output: Pandas DF containing columns:
                1. input_text: the input sentence | String
                2. doc: Spacy doc object of the sent analysis. See https://spacy.io/api/doc | Doc
                3. toponyms_found: Whether locations were found in the input sent | Bool
                4. locations: locations in the input text, if found | list of strings or None
                5. topo_lemmas: lemmatized versions of the locations | list of strings or None
                6. topo_spans: the index of the start and end characters of the identified 
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
        
        # apply preprocessing step, if requested
        if preprocess:
            input_texts = [self.preprocess_sent(sent) for sent in tqdm(input_texts, desc="Preprocessing input...")]
        
        # run spacy pipeline 
        tag_results = list(tqdm(self.ner_pipeline.pipe(input_texts), total=len(input_texts), desc="Running toponym recognition..."))
        
        # gather the wanted features from spacy doc objects into a dictionary of lists
        tagged_sentences = [self.get_features(sent) for sent in tag_results]
        
        return self.to_dataframe(tagged_sentences, ids)
        """
        if self.output_df:
            return self.to_dataframe(tagged_sentences)
        else:
            return tagged_sentences
        """
            
    def get_features(self, doc):
        """Input: a sentence to tag (string)
        Output: a dictionary with the same variables as listed in 'tag_sentences'"""
        #doc = self.ner_pipeline(sent)
        
        # if the tagger created an output, i.e. at least one of the words in the input
        # was tagged, create an output of that. Otherwise, return a mostly empty dict
        #docs = []
        toponyms = []
        topo_labels = []
        topo_lemmas = []
        topo_spans = []
        toponyms_found = False

        # gather the NER labels found to a list 
        labels = [ent.label_ for ent in doc.ents]


        # looping through the entities, collecting required information
        # namely, the raw toponym text, its lemmatized form and the span as tuple
        for ent in doc.ents:
            if ent.label_ in self.entity_tags:
                # apply filtering if requested
                if self.filter_toponyms:
                    # length filtering 
                    if len(ent.text)>1:
                        toponyms.append(ent.text)
                        topo_labels.append(ent.label_)
                        
                        # remove hashtags, which mark word boundaries in compound words
                        lemma = ent.lemma_.replace("#","")
                        # in addition, remove punctuation characters, if they were captured by the tagger
                        # included are various quotation marks
                        lemma = re.sub(r'[.?!;:\'"“”‘’]', '', lemma)
                        
                        # add lemmatized versions of the toponyms to list 
                        topo_lemmas.append(lemma)
                        # spans; character start and end locations 
                        topo_spans.append((ent.start_char, ent.end_char))
                        toponyms_found = True
                else:
                    toponyms.append(ent.text)
                    topo_labels.append(ent.label_)
                    topo_lemmas.append(ent.lemma_.replace("#",""))
                    topo_spans.append((ent.start_char, ent.end_char))
                    toponyms_found = True
       #docs.append(doc)

        if toponyms_found:        
            doc_results = {'input_text': doc.text, 'toponyms': toponyms, 'topo_lemmas': topo_lemmas,
                            'topo_labels':topo_labels, 'topo_spans': topo_spans,'toponyms_found': toponyms_found}
        else:
            doc_results = {'input_text': doc.text, 'locations': None, 'topo_lemmas': None,
                    'topo_labels':None,'topo_spans': None, 'toponyms_found': toponyms_found}

        return doc_results
    
    def preprocess_sent(self, sent):
        """Optionally cleans up noise (especially prominent in social media posts): removes emojis (TODO), mentions (@xyz), hashtags (#, but not the content) and URLs.
        Based on work by Hiippala et al. 2020: Mapping the languages of Twitter in Finland: richness and diversity in space and time. See: https://zenodo.org/record/4279402
        """
        # Remove all mentions (@) in the input
        sent = re.sub(r'@\S+ *', '', sent)
        
        # remove hashes from hashtags
        sent = sent.replace('#', '')
        
        # remove old school heart emojis <3
        sent = sent.replace('<3', '')
        
        # remove ampersand (&), which may be followed by 'amp'
        sent = re.sub(r'&amp|&', '', sent)
        
        # remove URL's: i.e. remove everything that follows http(s) until a whitespace
        sent = re.sub(r'http[s]?://\S+', "", sent)
        
        return sent
        
        
    def to_dataframe(self, results, ids):
        df = pd.DataFrame(results)
        
        if ids:
            df['id'] = ids
            
        df['input_order'] = df.index
        
        # split the possible list contents into multiple rows
        if self.explode_df:
            df = df.apply(lambda x: x.explode() if x.name in ['toponyms', 'topo_labels', 'topo_lemmas', 'topo_spans'] else x)
        if self.drop_non_locs:
            return self.drop_non_locations(df)
        else:
            return df
    
    def drop_non_locations(self, df):
        """Remove input strings / rows where the tagger did not find any toponyms."""
        df = df[df['toponyms_found']]
        return df
