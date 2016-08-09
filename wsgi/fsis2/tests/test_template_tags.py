'''
=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/test_template_tags.py
Created: 25 Sep 2015 11:58:05


DESCRIPTION:



A. Cottrill
=============================================================
'''


import pytest

from fsis2.templatetags.fsis2_filters import *

def test_scrub_spc():
    '''the template filter scrub_spc take a full speceis name (include
    genus and species), strip them away, removes and spaces and turns the
    common name in lower case.
    '''
    nms = [
        'Sockeye Salmon (Oncorhynchus nerka)',
        'Chinook Salmon (Oncorhynchus tshawytscha)',
        'Rainbow Trout (Oncorhynchus mykiss)',
        'Brown Trout (Salmo trutta) ',
        'Brook Trout (Salvelinus fontinalis)',
        'Lake Trout (Salvelinus namaycush)',
        'Splake (Salvelinus fontinalis x Salvelinus namaycush)',
        'Lake Trout Backcross',
        'Muskellunge (Esox masquinongy)',
        'Smallmouth Bass (Micropterus dolomieu)',
        'Walleye (Sander vitreum)']

    shouldbe = ["sockeyesalmon",
                "chinooksalmon",
                "rainbowtrout",
                "browntrout",
                "brooktrout",
                "laketrout",
                "splake",
                "laketroutbackcros",
                "muskellunge",
                "smallmouthbass",
                "walleye",]

    for x,y in zip(nms,shouldbe):
        assert y == scrub_spc(x)


def test_prj_cd_Year():
    """the template fileter prj_cd_year() takes a project code, extracts
    the two digit year and returns the 4-digit year.

    """

    prj_cds = ['LHA_FS89_001',
              'LHA_FS90_001',
              'LHA_FS91_001',
              'LHA_FS92_001',
              'LHA_FS93_001',
              'LHA_FS94_001',
              'LHA_FS95_001',
              'LHA_FS96_001',
              'LHA_FS97_001',
              'LHA_FS98_001',
              'LHA_FS99_001',
              'LHA_FS00_001',
              'LHA_FS01_001',
              'LHA_FS02_001',
              'LHA_FS03_001',
              'LHA_FS04_001',
              'LHA_FS05_001',]

    shouldbe = ['1989', '1990', '1991', '1992', '1993', '1994',
                '1995', '1996', '1997', '1998', '1999', '2000',
                '2001', '2002', '2003', '2004', '2005', ]

    for x,y in zip(prj_cds,shouldbe):
        assert y == prj_cd_Year(x)


def test_format_cwt():
    """format_cwt takes a 6-digit cwt number and returns a string with
    three components of cwt number seperated by a hyphen.  """


    cwts = [ '635625', '630704', '635624', '513416', '431705',
             '630500', '631300', '513124', '631203', '431804',
             '016490', '640151', '051389', '634400', '630161']

    shouldbe = ['63-56-25','63-07-04','63-56-24','51-34-16','43-17-05',
                '63-05-00','63-13-00','51-31-24','63-12-03','43-18-04',
                '01-64-90','64-01-51','05-13-89','63-44-00','63-01-61']

    for x,y in zip(cwts,shouldbe):
        assert y == format_cwt(x)
