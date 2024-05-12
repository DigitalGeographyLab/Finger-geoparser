import sys
print(sys.path)

from fingerGeoparser import geoparser

def test_constructor():
    gp = geoparser.geoparser(pipeline_path="fi_core_news_sm")
    assert isinstance(gp, geoparser.geoparser)
    
def test_method():
    gp = geoparser.geoparser(pipeline_path="fi_core_news_sm")
    res = gp.geoparse(["Helsinki on kaunis tänään", "Paris Hilton mokasi."])
    
    #assert isinstance(gp, geoparser)
