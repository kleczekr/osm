#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import codecs
from collections import defaultdict
import pprint
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

'''
I decided to use a rather primitive mapping method -- it takes an entire street name,
and corrects it into a correct name. This solution was motivated by the fact, that there was
very few names in the set which demanded correction, and this solution was the most
efficient.
'''

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

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

'''
The following function is a slightly modified version of the one written by
Myles: https://discussions.udacity.com/t/changing-attribute-value-in-xml/44575/3

'''

def modify_xml(new_file):
    outfile = codecs.open(new_file, 'w')
    # outfile.write('<?xml version="1.0" encoding="UTF-8"?>')
    for event, elem in ET.iterparse(old_file, events=("start", "end")):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    tagtext = tag.attrib['v'].encode('utf-8')
                    if tagtext in mapping.keys():
                        print tagtext, '==>'
                        tag.set('v', mapping[tagtext])
                        print tag.attrib['v']
    outfile.write(ET.tostring(elem, encoding='UTF-8'))
    outfile.close()

'''
The program takes awfully long to run (on my computer, it munched the file
for over half an hour), but seems to work fine
'''
old_file = 'w.osm'
new_file = 'new_w.osm'
modify_xml(new_file)
