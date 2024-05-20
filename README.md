![Finger Geoparser logo](https://github.com/Tadusko/fi-geoparser/blob/master/FINGER_logo_transparent.png?raw=true "Finger logo")
## This project has had significant updates and rewrites recently.
## Updated documentation will be added in May 2024.

# Finger: Finnish geoparser
_Geoparsing_ is the process of finding location mentions (toponyms, aka. place names) in texts (toponym recognition or _geotagging_) and defining geographical representations, such as coordinate points, for them (toponym resolution or _geocoding_). Finger is a geoparser for Finnish texts. This program consists of three classes: the toponym recognizer, the toponym resolver, and the geoparser, which wraps the two previous modules.

### Toponym recognizer (geotagger)
The geotagger is built using [Spacy NLP library](https://spacy.io/) and it implements BERT-based language model for a more accurate representation of language and thus better results. The pipeline runs a complete linguistic analysis (part-of-speech tagging, morphological analysis, dependency parsing, token and sentence segmentation, lemmatization), but named entity recognition (NER) is the important part. Input texts' named locations, such as countries, lakes and important sights, are recognized, then returned to their base form using the lemmatizer. These results are passed on to the geocoder.

### Toponym resolver (geocoder)
The geocoder currently simply queries the [GeoNames](https://www.geonames.org/) gazetteer using the Python library [Geocoder](https://geocoder.readthedocs.io/) and outputs coordinate points, if matches are found. I plan to expand this functionality in the future.

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


Other resources used in either the pipeline or this code:
 - [FinBERT](https://turkunlp.org/finnish_nlp.html#finbert) language model by TurkuNLP, CC BY 4.0. See [Virtanen, Kanerva, Ilo, Luoma, Luotolahti, Salakoski, Ginter and Pyysalo; 2019](https://arxiv.org/pdf/1912.07076.pdf)
 - [Turku NER Corpus](https://github.com/TurkuNLP/turku-ner-corpus) by TurkuNLP, CC BY 4.0. See [Luoma, Oinonen, Pyykönen, Laippala and Pyysalo; 2020](https://www.aclweb.org/anthology/2020.lrec-1.567.pdf)
 - [Spacy-fi pipeline](https://github.com/aajanki/spacy-fi) by Antti Ajanki, MIT License.

### TODO
 - ~~Alter the output so that each successfully geoparsed toponym is in a row of its own. Toponyms from the same input can be connected with an id from another column.~~
 - ~~Add toponym's location in the input, e.g. character span in the input string from start to end, as a column.~~
 - Package this project and make it pip-installable. Overall, make installation and usage more straightforward.
 - Learn more about and implement tests.
 - Some sort of config file or argument parser instead of passing parameters to the _geoparse_ method?
 - Test out the lemmatizer more. I think it might've problems with rarer place names. Like _Vesijärvellä_ is fine, but _Joutjärvellä_ doesn't get lemmatized. Extend dictionary or implement another type of lemmatizer?
 - Implement a Voikko-based typo checker and fixer.
 - Implement gazetteers/API's other than GeoNames. [Nimisampo](https://nimisampo.fi/fi/app) has potential in the Finnish context.
 - ~~Implement text-preprocessing steps. Removing hashtags for instance?~~ Rudimentary filtering of impossibly short toponyms added. Seems to work well.
 - Implement geocoding / toponym resolution step other than a simple query. The literature should provide hints.
 - Use the linguistic pipeline results (stored in the doc object) in some way. Useful in toponym resolution?
 - ~~Add an _identifier_ keyword argument. If this is present, it'll be added to the output df and can be used to identify the individual inputs (e.g. tweets by id, texts by their writer). Maybe require a list that's as long as the input list? So that each id is assumed to be in the same index as each input.~~
 - Allow the user to limit the spatial extent of their geoparsing results by passing a bbox when calling _geoparse_
 - Rewrite geocoding: for now, move it to use geopandas/geopy instead of Geocoder
