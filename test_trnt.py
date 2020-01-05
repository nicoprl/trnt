#!/usr/bin/python3

from trnt import *

def test_get_token():
    tkn = get_token(
        "https://torrentapi.org/pubapi_v2.php", 
        "trnt", 
        {"user-agent": "trnt"}
    )
    assert type(tkn) is str
    assert len(tkn) > 0

def test_search_torrent():
    found = search_torrent(
        "The.Office.S02",
        "https://torrentapi.org/pubapi_v2.php", 
        "trnt", 
        {"user-agent": "trnt"},
        log
    )

    assert type(found) is dict
    assert len(found) > 0
    assert type(found[0]) is list
    assert found[0][0] == "The.Office.US.S02.WEBRip.x264-FGT"