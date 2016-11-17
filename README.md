# Data Wrangling with Python and SQL
### openStreetMap project

The following is an attempt at wrangling the Open Street Map of Warsaw, Poland, as I lived there during my study years, and I know it rather well.

The data was downloaded from the website of the [Map Zen](https://mapzen.com/data/metro-extracts/metro/warsaw_poland/) project.

## Problems encountered in the data

Running the data.py function on the OSM file for Warsaw indicated the following problems:

- 'city.simc' field in the data, which had ambiguous meaning
- Some street names have numbers in them. I would like to check these, and see, if something should be done about them.
- Some postal codes contained in the file seem to belong to cities from different administrative districts.
- Some of the fields have input in non-Latin scripts (predominantly Russian, but also some Asian scripts which I have not yet identified). I would like to see these, and check, whether something should be done about these (providing transliteration etc.).

## The SIMC number

After running the data.py function on the XML file and taking a look at the output, I noticed a confusing field referring to the cities, namely 'city:simc', containing a number:

```XML
<tag k="addr:city" v="Warszawa" />
<tag k="addr:street" v="Stefana Żeromskiego" />
<tag k="source:addr" v="mapa.um.warszawa.pl" />
<tag k="addr:postcode" v="05-075" />
<tag k="addr:city:simc" v="0921728" />
```
As I was not acquainted with it (it was different from postcode, as you can se above), I found out it refers to territorial classification of Poland, TERYT. The government statistical portal of Poland contained [an XML file](http://www.stat.gov.pl/broker/access/prefile/listPreFiles.jspa) of all SIMC numbers of Polish cities. In an attempt at corroborating, and possibly correcting, the SIMC numbers in OSM, I wrote the following function, converting the SIMC XML to CSV:

```python
import csv
import xml.etree.cElementTree as ET
import codecs
import sys    # sys.setdefaultencoding is cancelled by site.py
reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')

outputs = 'simc.csv'

tree = ET.parse('SIMC.xml')
root = tree.getroot()

SIMC_FIELDS = ['name', 'sym', 'sympod']

with codecs.open(outputs, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(SIMC_FIELDS)
    for child in root:
        for stuff in child:
            for element in stuff:
                if element.attrib['name'] == 'NAZWA':
                    name = element.text
                elif element.attrib['name'] == 'SYM':
                    sym = element.text
                elif element.attrib['name'] == 'SYMPOD':
                    sympod = element.text
            writer.writerow((name, sym, sympod))
```
This outputs a 'simc.csv' file, which I then imported into SQL with this adapted call:

```SQL
CREATE TABLE simc (
    name TEXT NOT NULL,
    sym INTEGER NOT NULL,
    sympod INTEGER NOT NULL
);
```

I used the [data wrangling schema](https://gist.github.com/swwelch/f1144229848b407e0a5d13fcb7fbbd6f) provided by Udacity team to import into SQL the other .csv files.

After importing all the files to a single database, I performed the following query to see if the SIMC numbers from the government file match the ones in the OSM:

```SQL
SELECT DISTINCT simc.sym, simc.name, number.value, name.value
FROM simc JOIN (ways_tags number JOIN ways_tags name ON number.id = name.id)
ON simc.sym = number.value
WHERE number.key = 'city:simc'
AND name.key = 'city';
```

As the output of the above is too long to check it manually, I ran it again, to output only lines where the name from the first file was different from the name from the second file:

```SQL
SELECT DISTINCT simc.sym, simc.name, number.value, name.value
FROM simc JOIN (ways_tags number JOIN ways_tags name ON number.id = name.id)
ON simc.sym = number.value
WHERE number.key = 'city:simc'
AND name.key = 'city'
AND simc.name != name.value;
```

This output only one line:

```SQL
921728|Wesoła|0921728|Warszawa
```

As indicated by the [Wikipedia page devoted to 'Wesoła'](https://en.wikipedia.org/wiki/Wesoła), the place is now considered to be part of Warsaw, but was an independent town prior to 2002. This clarifies, why the government file lists the SIMC number of Wesoła as referring to Warsaw, while the OSM map lists it as an independent entity.

## Street names

As I explored street names, I was quite surprised to find no major mistakes or abbreviations. It might have been caused by the convention used in Polish edition of the OSM, where there is no equivalent of the 'Street' noun used by the street names (in Polish, it is put before the name of the street, and conventionally abbreviated to 'Ul.'). In some names, there is the abbreviation 'im.' from the word 'imienia' ('named after'), but I chose not to alter it, as it is used consistently.

I did notice, though, that some streets have numbers in them. I ran a Python script on the ways_tags.csv to output all the street names containing numbers:

```python
import csv

def numbers(s):
    return any(i.isdigit() for i in s) # The function finding numbers in strings is taken from SO

with open('ways_tags.csv') as f:
    reader = csv.DictReader(f)
    new_set = set()
    for row in reader:
        if row['key'] == 'street' and numbers(row['value']):
            new_set.add(row['value'])
    for value in new_set:
        print unicode(value, 'utf-8').encode('utf-8')
```

The function prints values containing number in them. Majority of the values are acceptable, as the numbers are part of the street names, e.g. '6 Pułku Piechoty' or '1863 Roku'. In some cases the use of numbers seems misleading: 'Powstańców Warszawy 19', 'Powstańców Warszawy 17', 'Karczewska 14/16', 'Ireny Kosmowskiej - Grodzieńska 21/29'. I ran a simple script counting occurences of the above in the entire map:

```python
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
    print strange_names_dict
```

In spite of all my pains, the output is still not displaying unicode characters. Anyway, it looks like that:

```python
{'Powsta\xc5\x84c\xc3\xb3w Warszawy 17': 1,
'Karczewska 14/16': 1,
'Ireny Kosmowskiej - Grodzie\xc5\x84ska 21/29': 1,
'Powsta\xc5\x84c\xc3\xb3w Warszawy 19': 1}
```

And indicates, that each of the problematic names occurs only once in the entire map. As the above names do not denote street names, but entire addresses, they can be removed from the map.


## Postal codes

Postal codes in Mazovian district, in which Warsaw is located, begin with 0. As I noticed, that some of the numbers in abbreviated files deviate from this pattern, I decided to run a script finding the deviant postal codes:

```python
import csv

with open('ways_tags.csv') as f:
    reader = csv.DictReader(f)
    deviant_codes = set()
    for row in reader:
        code = row['value']
        if row['key'] == 'postcode' and int(code[0]) != 0:
            deviant_codes.add(code)
    print deviant_codes
```

The code outputs the following set:

```python
set(['96-314', '96-315', '96-316', '96-300', '91-065', '26-914', '96-313', '96-102', '96-515', '96-516', '96-111', '96-321', '96-320', '96-330', '96-325', '96-323'])
```

After a while of searching for details online, I established, that postcodes beginning with '96' also belong to Masovian district. There are two other types of codes left in the set: '26-914' and '91-065'. The first one, '26-914', is also located in Masovian district. The second one, '91-065', is located in the neighbouring Lodz district, and should be corrected.

## Non-Latin characters in the map

As I mentioned, I discovered, that there are fields in the data containing non-Latin characters, predominantly Russian. As I have been looking for ways of finding these fields, I came upon a [StackOverflow post](http://stackoverflow.com/questions/3094498/how-can-i-check-if-a-python-unicode-string-contains-non-western-letters) containing code for checking string for non-Latin characters. Below is the code I adapted for checking the map data:

```python
import unicodedata as ud

latin_letters= {}

def is_latin(uchr):
    try: return latin_letters[uchr]
    except KeyError:
         return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))

def only_roman_chars(unistr):
    return all(is_latin(uchr)
           for uchr in unistr
           if uchr.isalpha())
```

## Sources used in this project
- [StackOverflow post on converting Unicode](http://stackoverflow.com/questions/13485546/converting-unicode-to-in-python)
- [StackOverflow post on converting XML to CSV](http://stackoverflow.com/questions/31844713/python-convert-xml-to-csv-file)
- [StackOverflow post on checking a string for non-Latin characters](http://stackoverflow.com/questions/3094498/how-can-i-check-if-a-python-unicode-string-contains-non-western-letters)
- [StackOverflow AlKid's solution to the function finding numbers in strings](http://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number)
- [SQLite documentation on importing CSV files](https://www.sqlite.org/cvstrac/wiki?p=ImportingFiles)
- [ElementTree documentation](https://docs.python.org/2/library/xml.etree.elementtree.html)
- [Python CSV module documentation](https://docs.python.org/2/library/csv.html)
- [Wikipedia article on postal codes in Poland](https://en.wikipedia.org/wiki/Postal_codes_in_Poland)
- [Online search engine for postal codes in Poland](http://kody.jzk.pl/)
