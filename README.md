![Finger Geoparser logo](https://github.com/DigitalGeographyLab/Finger-geoparser/blob/master/FINGER_logo_transparent.png?raw=true "Finger logo")

# Finger: the Finnish geoparser
## Overview
_Geoparsing_ is the process of finding location mentions (toponyms, aka. place names) in texts (toponym recognition or _geotagging_) and defining geographical representations, such as coordinate points, for them (toponym resolution or _geocoding_). Finger is a geoparser for Finnish texts. For toponym recognition, Finger uses a fine-tuned model trained for the [Spacy NLP library](https://spacy.io/). The same model _lemmatizes_ recognized toponyms, that is, transforms them to a base form (_Helsingissä_ –> _Helsinki_). Finally, the lemmatized toponyms are resolved to locations by querying a geocoder. Currently, we upkeep a geocoder based on [_Pelias_](https://www.pelias.io/). This program consists of three classes: the toponym recognizer, the toponym resolver, and the geoparser, which wraps the two previous modules. It uses a language model fine-tuned for extracting place names and a geocoder service for locating them.

## Tiivistelmä suomeksi
_Geojäsentäminen_ viittaa paikannimien löytämiseen ja paikantamiseen jäsentelemättömistä teksteistä. _Finger_ on Python-ohjelmisto suomenkielisten tekstiaineistojen geojäsentämiseen. Paikannimien tunnistaminen ja perusmuotoistaminen (esim. _Helsingistä_ –> _Helsinki_) tehdään [spaCy-kirjaston]((https://spacy.io/)) avulla. Paikannimien sijainnin ratkaiseminen on [Pelias-geokoodarilla](https://www.pelias.io/). Ylläpidämme toistaiseksi _[Pelias-geokoodariin](https://www.pelias.io/)_ perustuvaa geokoodauspalvelua, jota Finger käyttää oletuksena, CSC:n Puhti-palvelussa.

## Getting started
Finger is available through [pypi](https://pypi.org/project/fingerGeoparser/).

### Installation
I highly recommend creating a virtual environment for Finger (e.g., [venv](https://docs.python.org/3/tutorial/venv.html) or [conda](https://docs.conda.io/projects/conda/en/latest/index.html) to prevent clashes with other packages – the versions used by Finger are not necessarily the latest ones.

 ```python
pip install fingerGeoparser
 ```
Next, a spaCy model (pipeline) that has been trained for named-entity recognition and lemmatization is needed. Any pipelines that meet these requirements are fine. For example, spaCy offers [pre-trained pipelines for Finnish](https://spacy.io/models/fi/).

Alternatively, we have trained a model based on [Finnish BERT](https://huggingface.co/TurkuNLP/bert-base-finnish-cased-v1). This is a transformers-based model Download the from _Releases_ or pip install it directly like this:

  ```python
 pip install https://github.com/DigitalGeographyLab/Finger-geoparser/releases/download/0.2.0/fi_fingerFinbertPipeline-0.1.0-py3-none-any.whl
 ```

### Usage example
 ```python
from fingerGeoparser import geoparser

# initializing the geoparser
# model name (if it has been pip installed) or path is provided; in this example, we use spaCy's small pretrained model
gp = geoparser.geoparser(pipeline_path="fi_core_news_sm")

# defining inputs
input_texts = ["Olympialaiset järjestettiin sinä vuonna Helsingissä.", "Paris Hilton on maailmanmatkalla"]

res = gp.geoparse(input_texts)

 ```
_res_ contains a [Pandas dataframe](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) with various columns of information (see _Data model_ below)


If you want to find out more about the geoparser and the input parameters, call
```python
help(geoparser)
```

### Data model
Currently, the program accepts strings or lists of strings as input. The input is assumed to be in Finnish and segmented to short-ish pieces (so that the input isn't for example a whole book chapter as a string). 

Most users will want to use the _geoparser_ module, as it wraps geoparsing pipeline and functions under a simple principle: text in, results out. [See below for an example](#usage-example). The output of the process is a [_Pandas dataframe_](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) with the following columns:

| Column header | Description | Data type | Example |
| --- | --- | --- | --- |
| input_text | The input sentence | *string* | "Matti Järvi vietti tänään hienon päivän Lahdessa" |
| input_order | The index of the inserted texts. i.e. the first text is 0, the second 1 etc. | *int* | 0 |
| toponyms_found | Whether locations were found in the input sent | *boolean* | True |
| toponyms | Location tokens in the original wordform, if found | *(list of) string(s)* or *none* | "Lahdessa" |
| topo_lemmas | Lemmatized versions of the toponyms | *(list of) string(s)* or *none* | "Lahti" |
| topo_spans | index of the start and end characters of the identified toponyms in the input text string | *tuple* | (40, 48) |
| names | Versions of the locations returned by querying GeoNames | *(list of) string(s)* or *none* | "Lahti" |
| coordinates | Long/lat coordinate points in WGS84 | (*list of*) *tuple(s)* or *none* | (25.66151, 60.98267) |
| bbox | \[Minx, miny, maxx, maxy] bounding box of the location, if available | (*list of*) *list(s)* | \[25.5428275, 60.9207905391, 25.8289352655, 61.04401] |
| gid | Unique identifier given by the geocoder. | (*list of*) *string(s)* | 	"whosonfirst:locality:101748425" |
| label | Label given by the geocode. | (*list of*) *strings* | "Lahti, Finland" |
| layer | Type of location based on Who's on First [placetypes](https://github.com/whosonfirst/whosonfirst-placetypes) | (*list of*) *string(s)* | "country" |
| * id |The identifying element, like tweet id, tied to each input text. Optional | *string*, *int*, *float* | "first_sentence" |


NOTE. The data model still subject to change as the work progresses.

### License and credits
The source code is licensed under the MIT license.

This geoparser was developed by Tatu Leppämäki of the Digital Geography Lab, University of Helsinki. Find me on [Mastodon](https://mstdn.social/@tadusko) and [Twitter](https://twitter.com/Tadusk0).


Other resources used in either the pipeline or this code:
 - [Finnish BERT](https://turkunlp.org/finnish_nlp.html#finbert) language model by TurkuNLP, CC BY 4.0. See [Virtanen, Kanerva, Ilo, Luoma, Luotolahti, Salakoski, Ginter and Pyysalo; 2019](https://arxiv.org/pdf/1912.07076.pdf)
 - [Turku NER corpus](https://github.com/TurkuNLP/turku-ner-corpus) by TurkuNLP, CC BY 4.0. See [Luoma, Oinonen, Pyykönen, Laippala and Pyysalo; 2020](https://www.aclweb.org/anthology/2020.lrec-1.567.pdf)
 - [UD_Finnish TDT corpus](https://github.com/UniversalDependencies/UD_Finnish-TDT/tree/master) CC BY SA 4.0. See [Haverinen et al. 2014](http://dx.doi.org/10.1007/s10579-013-9244-1); [Pyysalo et al. 2015](https://aclweb.org/anthology/W/W15/W15-1821.pdf)
(Older versions)
 - [Spacy-fi pipeline](https://github.com/aajanki/spacy-fi) by Antti Ajanki, MIT License.

### Citation
If you use the geoparser or related resources in a scientific publication, please cite the following article:
```
@article{doi:10.1080/13658816.2024.2369539,
author = {Tatu Leppämäki, Tuuli Toivonen and Tuomo Hiippala},
title = {Geographical and linguistic perspectives on developing geoparsers with generic resources},
journal = {International Journal of Geographical Information Science},
volume = {0},
number = {0},
pages = {1--22},
year = {2024},
publisher = {Taylor \& Francis},
doi = {10.1080/13658816.2024.2369539},
URL = {https://doi.org/10.1080/13658816.2024.2369539}
}
```

