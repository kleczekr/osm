#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

mapping = {
    'Zadumana 1A': 'Zadumana',
    'Belwederska 20/22': 'Belwederska',
    'Nowy Drzewicz 62': 'Nowy Drzewicz',
    'Sokołowska 9/U31': 'Sokołowska',
    'Nowoursynowska 154A': 'Nowoursynowska',
    'Wiejska 1': 'Wiejska',
    'Powstańców Warszawy 19': 'Powstańców Warszawy',
    'Powstańców Warszawy 17': 'Powstańców Warszawy',
    'Karczewska 14/16': 'Karczewska',
    'Postępu 14': 'Postępu',
    'Ireny Kosmowskiej - Grodzieńska 21/29': 'Ireny Kosmowskiej - Grodzieńska'
}

'''
The program takes the newly corrected file, and checks if there are any old incorrect
names left, to evaluate, if the correcting script did its job.
'''

osm_file = open('new_w.osm', "r")

for event, elem in ET.iterparse(osm_file, events=("start",)):

    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if is_street_name(tag):
                tagtext = tag.attrib['v']
                if tagtext in mapping.keys():
                    print tagtext
osm_file.close()