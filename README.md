# Finnish geoparser
_Geoparsing_ is the process of finding location mentions in texts (_geotagging_) and defining geographical representations, such as coordinate points, for them (_geocoding_). This is the first implementation of a Finnish geoparser, built on state-of-the-art methods yet using established Python libraries.

### Geotagger
The geotagger is built using [Spacy NLP library](https://spacy.io/) and it implements BERT-based language model for a more accurate representation of language and thus better results. The pipeline runs a complete linguistic analysis (part-of-speech tagging, morphological analysis, dependency parsing, token and sentence segmentation, lemmatization), but named entity recognition (NER) is the important part. Input texts' named locations, such as countries, lakes and important sights, are recognized, then returned to their base form using the lemmatizer. These results are passed on to the geocoder.

### Geocoder
The geocoder currently simply queries the [GeoNames](https://www.geonames.org/) gazetteer using the Python library [Geocoder](https://geocoder.readthedocs.io/) and outputs coordinate points, if matches are found. I plan to expand this functionality in the future.


## Usage
The package isn't currently on any packaging index (pip, conda) and must thus be copied from this source. There are number of preparation steps involved to use this pipeline.
### Preparations
 - Copy this repo with for example downloading the zip version. 
 - pip install the requirements.txt file (hopefully has everything needed)
 - Install Spacy pipeline. NOTE The installation file isn't currently publicly available (I've shared it in Slack).
   - Download the roughly 1 GB tar.gz file and install by pip install on the file. This should add a package called _fi\_geoparser_ on your current environment. It can be loaded simply by calling spacy.load('fi_geoparser')
 - [Voikko](https://voikko.puimula.org/) is used for lemmatizing the input texts. It requires downloading a dictionary file (all OS's) and DLL file (on Windows). Follow the instructions listed [here](https://voikko.puimula.org/python.html).
   - NOTE getting the DLL to work on Windows can be a hassle. I had to add path to the file as a system path.
 - Create a [GeoNames](https://www.geonames.org/) account. The account's username is used as an API key when querying GN.
### Usage example
Python interpreter is started in the Finnish geoparser folder and in an environment with the required installations.

```python
>>>from geoparser import geoparser
>>>parser = geoparser(gn_username='my_username')
>>>input = ["Matti Järvi vietti tänään hienon päivän Lahden Messilässä", "Olympialaisten avajaiset tekstitettiin suomen kielelle"]
>>>results = parser.geoparse(input)
Starting geotagging...
Finished geotagging. 1 out of 2 sentences found to have locations mentioned.
Geocoding done, returning dataframe.
Total elapsed time: 0.33 s
>>>print(results[['loc_lemmas','gn_coord_points']])
         loc_lemmas                               gn_coord_points
0  [Lahti, Messilä]  [(25.66151, 60.98267), (25.56667, 61.01667)]
1              None                                          None
```

### License and credits
The source code is licensed under the MIT license.

 - [FinBERT](https://turkunlp.org/finnish_nlp.html#finbert) language model by TurkuNLP, CC BY 4.0. See [Virtanen, Kanerva, Ilo, Luoma, Luotolahti, Salakoski, Ginter and Pyysalo; 2019](https://arxiv.org/pdf/1912.07076.pdf)
 - [Turku NER Corpus](https://github.com/TurkuNLP/turku-ner-corpus) by TurkuNLP, CC BY 4.0. See [Luoma, Oinonen, Pyykönen, Laippala and Pyysalo; 2020](https://www.aclweb.org/anthology/2020.lrec-1.567.pdf)
 - [Spacy-fi pipeline](https://github.com/aajanki/spacy-fi) by Antti Ajasti, MIT License.

### TODO
- add to do
