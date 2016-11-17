#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv

import sys    # sys.setdefaultencoding is cancelled by site.py
reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')

strange_names = [unicode('Powstańców Warszawy 19', 'utf-8').encode('utf-8'), unicode('Powstańców Warszawy 17', 'utf-8').encode('utf-8'), unicode('Karczewska 14/16', 'utf-8').encode('utf-8'), unicode('Ireny Kosmowskiej - Grodzieńska 21/29', 'utf-8').encode('utf-8')]

with open('ways_tags.csv') as f:
    strange_names_dict = {unicode('Powstańców Warszawy 19', 'utf-8').encode('utf-8'): 0,
    unicode('Powstańców Warszawy 17', 'utf-8').encode('utf-8'): 0,
    unicode('Karczewska 14/16', 'utf-8').encode('utf-8'): 0,
    unicode('Ireny Kosmowskiej - Grodzieńska 21/29', 'utf-8').encode('utf-8'): 0}

    reader = csv.DictReader(f)
    
    for row in reader:
        name = row['value']
        if row['key'] == 'street' and name in strange_names:
            strange_names_dict[name] += 1

    for key in strange_names_dict.keys():
        print key + ': ' + str(strange_names_dict[key])