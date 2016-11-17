#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unicodedata as ud
import csv
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

latin_letters = {}


def is_latin(uchr):
    try: return latin_letters[uchr]
    except KeyError:
         return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))

def only_roman_chars(unistr):
    return all(is_latin(uchr)
           for uchr in unistr
           if uchr.isalpha())



with open('ways_tags.csv') as f:
    reader = csv.DictReader(f)
    not_romans = {}
    count = 0
    for row in reader:
        for field in row.values():
            if not only_roman_chars(unicode(field, 'utf-8')):
                if field in not_romans.keys():
                    not_romans[field] += 1
                else:
                    not_romans[field] = 1
    for item in not_romans.keys():
        if not_romans[item] > 5:
            print item + ': ' + str(not_romans[item])