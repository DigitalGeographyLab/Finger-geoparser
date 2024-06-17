![Finger Geoparser logo](https://github.com/DigitalGeographyLab/Finger-geoparser/blob/master/FINGER_logo_transparent.png?raw=true "Finger logo")
## This project has had significant updates and rewrites recently.
## Documentation will be updated over June.

# Finger: the Finnish geoparser
## Overview
_Geoparsing_ is the process of finding location mentions (toponyms, aka. place names) in texts (toponym recognition or _geotagging_) and defining geographical representations, such as coordinate points, for them (toponym resolution or _geocoding_). Finger is a geoparser for Finnish texts. For toponym recognition, Finger uses a fine-tuned model of the [Spacy NLP library](https://spacy.io/).  This program consists of three classes: the toponym recognizer, the toponym resolver, and the geoparser, which wraps the two previous modules. It uses a language model fine-tuned for extracting place names and a geocoder service for locating them.

### Toponym recognizer (geotagger)
The geotagger is built using [Spacy NLP library](https://spacy.io/). The pipeline first recognizes place names using a named entity recognition (NER) tagger, then extracts lemmatized versions of the recognized toponyms. These results are passed on to the geocoder.

### Toponym resolver (geocoder)
The geocoder queries a geocoder online services based on Pelias

### Data model
Currently, the program accepts strings or lists of strings as input. The input is assumed to be in Finnish and segmented to short-ish pieces (so that the input isn't for example a whole book chapter as a string). 

Most users will want to use the _geoparser_ module, as it wraps geoparsing pipeline and functions under a simple principle: text in, results out. [See below for an example](#usage-example). The output of the process is a [_Pandas dataframe_](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) with the following columns:

| Column header | Description | Data type | Example |
| --- | --- | --- | --- |
| input_text | The input sentence | *string* | "Matti Järvi vietti tänään hienon päivän Lahdessa" |
| input_order | The index of the inserted texts. i.e. the first text is 0, the second 1 etc. | *int* | 0 |
| doc | Spacy doc object of the sent analysis | [*doc*](https://spacy.io/api/doc) | Matti Järvi vietti tänään hienon päivän Lahdessa |
| locations_found | Whether locations were found in the input sent | *boolean* | True |
| locations | Location tokens in the og wordform, if found | *(list of) string(s)* or *none* | "Lahdessa" |
| loc_lemmas | Lemmatized versions of the locations | *(list of) string(s)* or *none* | "Lahti" |
| loc_spans | index of the start and end characters of the identified locations in the input text string | *tuple* | (40, 48) |
| names | Versions of the locations returned by querying GeoNames | *(list of) string(s)* or *none* | "Lahti" |
| coord_points | Long/lat coordinate points in WGS84 | (*list of*) *tuple(s)*, *Shapely Point(s)* or *none* | (25.66151, 60.98267) |
| * id |The identifying element, like tweet id, tied to each input text. Optional | *string*, *int*, *float* | "first_sentence" |


NOTE. There's some redundancy in the output currently. This is mostly because I want to cover every base at this point. The data model is still subject to change as the work progresses.

## Usage
There are number of preparation steps involved to use this geoparser.
### Preparations
 - I highly recommend creating [a virtual environment](https://docs.python.org/3/tutorial/venv.html) to prevent clashes with other packages.
 - Install Finger from [Pypi](https://pypi.org/project/fingerGeoparser/) with 
 ```python
pip install fingerGeoparser
 ```
 - This should install all the dependencies and the geoparser.
 - Next, you'll need the spaCy pipeline, which for example includes the fine-tuned BERT model. The pipeline wheel is released [here](https://github.com/Tadusko/finger-NLP-resources/releases/tag/v0.1.0). Simply install it like this:
  ```python
 pip install https://github.com/Tadusko/finger-NLP-resources/releases/download/v0.1.0/fi_geoparser-0.1.0-py3-none-any.whl
 ```
 - This adds the pipeline (*fi_geoparser*) in your pip environment.
 - [Voikko](https://voikko.puimula.org/) is used for lemmatizing (e.g. Turussa -> Turku) the input texts.
   - Using voikko may require downloading a dictionary file and a DLL file (on Windows). Follow the instructions listed [here](https://voikko.puimula.org/python.html) if you get voikko related errors.
   - NOTE getting the DLL to work on Windows can be a hassle. I had to add path to the folder with the DLL as a system path.
 - Create a [GeoNames](https://www.geonames.org/) account (or a few). The account's username is used as an API key when querying GN and is provided for Finger when geoparsing.

These steps need only be done once.
### Usage example
Python interpreter is started in the Finnish geoparser folder and in an environment with the required installations.

```python
>>>from geoparser import geoparser
>>>parser = geoparser(gn_username='my_username')
>>>input = ["Matti Järvi vietti tänään hienon päivän Lahden Messilässä", "Olympialaisten avajaiset tekstitettiin suomen kielelle"]
>>>results = parser.geoparse(input)
Starting geotagging...
Finished geotagging. 1 location hits found.
Starting geocoding...
Total elapsed time: 0.33 s
>>>print(results[['loc_lemmas','coord_points']])
         loc_lemmas                               coord_points
0  [Lahti, Messilä]  [(25.66151, 60.98267), (25.56667, 61.01667)]
1              None                                          None
```
If you want to find out more about the geoparser and the input parameters, call
```python
help(geoparser)
```

### License and credits
The source code is licensed under the MIT license.

### Citation
If you use this work in a scientific publication, please cite the following article:
```
(In the process of being published, I'll update this soon)
https://doi.org/10.1080/13658816.2024.2369539
```


Other resources used in either the pipeline or this code:
 - [FinBERT](https://turkunlp.org/finnish_nlp.html#finbert) language model by TurkuNLP, CC BY 4.0. See [Virtanen, Kanerva, Ilo, Luoma, Luotolahti, Salakoski, Ginter and Pyysalo; 2019](https://arxiv.org/pdf/1912.07076.pdf)
 - [Turku NER Corpus](https://github.com/TurkuNLP/turku-ner-corpus) by TurkuNLP, CC BY 4.0. See [Luoma, Oinonen, Pyykönen, Laippala and Pyysalo; 2020](https://www.aclweb.org/anthology/2020.lrec-1.567.pdf)
 - [Spacy-fi pipeline](https://github.com/aajanki/spacy-fi) by Antti Ajanki, MIT License.
