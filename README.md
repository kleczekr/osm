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

I take a closer look at these problems in phase 2 of the project, after introductory description of the dataset.

## Phase 1: description of the dataset

### Size of files containing data:

The files used in the project have the following size:
- warsaw.osm - 1,064,137,008 bytes
- ways.csv - 5,093,324 bytes
- ways_tags.csv - 62,672,605 bytes
- ways_nodes.csv - 123,713,407 bytes
- nodes.csv - 361,947,554 bytes
- nodes_tags.csv - 91,153,340 bytes
- SIMC.xml - 32,026,584 bytes
- simc.csv - 2,850,601 bytes
- mydb.db - 627,879,936 bytes

### Number of unique users:

```SQL
SELECT COUNT(DISTINCT(uid)) FROM nodes;
```
2368
```SQL
SELECT COUNT(DISTINCT(uid)) FROM ways;
```
1772

```SQL
SELECT COUNT(DISTINCT(new.uid))
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) AS new;
```

(The above code is, in its structure, not different from the one employed in the ['sample submission'](https://gist.github.com/carlward/54ec1c91b62a5f911c42#file-sample_project-md) file, linked to in the Udacity material. I tried to write different SQL queries, employing the JOIN command, but I came to the conclusion (after several code crashes) that UNION ALL, as explained [e.g. here,](https://www.techonthenet.com/sqlite/union_all.php) is necessary.)

2622

### 20 major contributors:

```SQL
SELECT new.user, COUNT(*) AS n
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) AS new
GROUP BY new.user
ORDER BY n DESC
LIMIT 5;
```
(The above code is, again, not much different from the code given in the ['sample submission'](https://gist.github.com/carlward/54ec1c91b62a5f911c42#file-sample_project-md) file, linked to in the Udacity material. As mentioned above, the UNION ALL operator seems to be necessary, and using it, it is difficult to write the query in radically different manner)

```SQL
rosomak|1221345
kocio|406644
Zibi-importy|185345
Madmaks|142099
balrog-kun-imports|135851
```

### Number of nodes and ways

```SQL
SELECT COUNT(DISTINCT(id)) FROM nodes;
```
4433235

```SQL
SELECT COUNT(DISTINCT(id)) FROM ways;
```
589328

### Number of most common node and way keys:

```SQL
SELECT key, COUNT(*) AS n
FROM nodes_tags
GROUP BY key
ORDER BY n DESC
LIMIT 6;
```

```SQL
housenumber|401708
street|336792
city|335089
postcode|334573
addr|256926
city:simc|184749
```

```SQL
SELECT key, COUNT(*) AS n
FROM ways_tags
GROUP BY key
ORDER BY n DESC
LIMIT 6;
```

```SQL
building|311286
highway|167694
housenumber|125745
city|124428
street|123576
postcode|118218
```

### Number of cafes, cinemas, and bars

```SQL
sqlite> SELECT value, COUNT(*) AS n
FROM nodes_tags
WHERE value = 'cafe'
GROUP BY value; 
```
487

```SQL
sqlite> SELECT value, COUNT(*) AS n
FROM nodes_tags
WHERE value = 'cinema'
GROUP BY value;
```
36

```SQL
sqlite> SELECT value, COUNT(*) AS n
FROM nodes_tags
WHERE value = 'bar'
GROUP BY value;
```
138


## Phase 2: auditing and cleaning the dataset

### Creating a database

While it might be somewhat counterintuitive to create a database before cleaning the data, I had to do so in order to perform SQL queries on it. For this purpose, I adapted solution [proposed on the forum by Myles](https://discussions.udacity.com/t/creating-db-file-from-csv-files-with-non-ascii-unicode-characters/174958/7) for creating a database for XML having Unicode signs. The code for importing the CSV to a database is available [here](https://github.com/kleczekr/osm/blob/master/python_files/database.py).

### The SIMC number

After running the data.py function on the XML file and taking a look at the output, I noticed a confusing field referring to the cities, namely 'city:simc', containing a number:

```XML
<tag k="addr:city" v="Warszawa" />
<tag k="addr:street" v="Stefana Żeromskiego" />
<tag k="source:addr" v="mapa.um.warszawa.pl" />
<tag k="addr:postcode" v="05-075" />
<tag k="addr:city:simc" v="0921728" />
```
As I was not acquainted with it (it was different from postcode, as you can se above), I found out it refers to territorial classification of Poland, TERYT. The government statistical portal of Poland contained [an XML file](http://www.stat.gov.pl/broker/access/prefile/listPreFiles.jspa) of all SIMC numbers of Polish cities. In an attempt at corroborating, and possibly correcting, the SIMC numbers in OSM, I wrote the function [simc_converter](https://github.com/kleczekr/osm/blob/master/python_files/simc_converter.py), which converts chosen fields from the XML file to a CSV document. The code outputs a 'simc.csv' file, which I then imported into SQL with this adapted call:

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

### Street names

As I explored street names, I was quite surprised to find no major mistakes or abbreviations. It might have been caused by the convention used in Polish edition of the OSM, where there is no equivalent of the 'Street' noun used by the street names (in Polish, it is put before the name of the street, and conventionally abbreviated to 'Ul.'). In some names, there is the abbreviation 'im.' from the word 'imienia' ('named after'), but I chose not to alter it, as it is used consistently.

I did notice, though, that some streets have numbers in them. I ran a Python script on the ways_tags.csv to output all the street names containing numbers ([the code is available here](https://github.com/kleczekr/osm/blob/master/python_files/numbers.py)).

The function displayed values containing at least one number in them. Majority of the values are acceptable, as the numbers are part of the street names, e.g. '6 Pułku Piechoty' or '1863 Roku'. In some cases the use of numbers seems misleading: 'Powstańców Warszawy 19', 'Powstańców Warszawy 17', 'Karczewska 14/16', 'Ireny Kosmowskiej - Grodzieńska 21/29'. I ran a [simple script counting occurences of the above in the entire map](https://github.com/kleczekr/osm/blob/master/python_files/strange_names.py), which output the following dictionary:

```python
Powstańców Warszawy 17: 1
Karczewska 14/16: 1
Ireny Kosmowskiej - Grodzieńska 21/29: 1
Powstańców Warszawy 19: 1
```

The output indicates, that each of the problematic names occurs only once in the entire map. As the above names do not denote street names, but entire addresses, they should be corrected. Below is the script I used to correct the mentioned entries in the XML file of the map (the code is also available [here](https://github.com/kleczekr/osm/blob/master/python_files/numbers_change_fixed_finally.py)). As I mention in a comment in the code, it is a slightly adapted code provided [by Myles in the forum thread](https://discussions.udacity.com/t/changing-attribute-value-in-xml/44575/3):

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import codecs
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
```

After running the code, I ran a simple script checking, if there are any names left from the group that was meant to be corrected. The script is available [here](https://github.com/kleczekr/osm/blob/master/python_files/reality_check.py), and returned no output---the script changing street names was successful.

### Postal codes

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
set(['96-314', '96-315', '96-316', '96-300', '91-065', '26-914',
'96-313', '96-102', '96-515', '96-516', '96-111', '96-321',
'96-320', '96-330', '96-325', '96-323'])
```

After a while of searching for details online, I established, that postcodes beginning with '96' also belong to Masovian district. There are two other types of codes left in the set: '26-914' and '91-065'. The first one, '26-914', is also located in Masovian district. The second one, '91-065', is located in the neighbouring Lodz district. As the value should, most likely, be corrected, we need to learn more about this object. The following query displays all the objects having the same ID as the mysterious postcode:

```SQL
sqlite> SELECT id, key, value
FROM ways_tags
WHERE id = (SELECT DISTINCT id
FROM ways_tags
WHERE value = '91-065');
```

The output is a single object:

```SQL
31102991|name|Kaponiera Pierwszego Bastionu
31102991|source|wikipedia
31102991|building|yes
31102991|postcode|91-065
```

The object is 'Kaponiera Pierwszego Bastionu', located in Cytadela Warszawska, and the proper postcode for it is 01-532. Writing a script editing and saving the XML file might seem futile when it is a single value that needs changing, and I chose to overwrite the value in the CSV file ways_tags.csv. The following script overwrites the value (it is a slightly edited version of the code provided in [this StackOverflow post](http://stackoverflow.com/questions/11033590/change-specific-value-in-csv-file-via-python)):

```python
import csv
r = csv.reader(open('ways_tags.csv'))

lines = [l for l in r]
lines_count = -1
for line in lines:
    lines_count += 1
    fields_count = -1
    for field in line:
        fields_count += 1
        if field == '91-065':
            lines[lines_count][fields_count] = '01-532'

writer = csv.writer(open('ways_tags_corrected.csv', 'w'))
writer.writerows(lines)
```

### Non-Latin characters in the map

As I mentioned, I discovered, that there are fields in the data containing non-Latin characters, predominantly Russian. As I have been looking for ways of finding these fields, I came upon a [StackOverflow post](http://stackoverflow.com/questions/3094498/how-can-i-check-if-a-python-unicode-string-contains-non-western-letters) containing code for checking string for non-Latin characters. After running the script, I received the following output:

```python
ヴィスワ
Президентский дворец в Варшаве
Міст Понятовського
Варшавская школа экономики
Посольство України
(...)
Піонерська вулиця
נמל התעופה ורשה פרדריק שופן
부크
```
As the output indicates, majority of the fields writen in non-Latin scripts are written in either Russian, or Ukrainian. This might not be a problem, since the list is not very long. We can take a look at how often these names are used. The following prints the names which occur more than five times (the code is also available [here](https://github.com/kleczekr/osm/blob/master/python_files/roman.py)):

```python
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
    # The loop below is included in order to display Unicode characters properly
    for item in not_romans.keys():
        if not_romans[item] > 5:
            print item + ': ' + str(not_romans[item])
```

The output is as follows:

```python
ヴィスワ: 9
Пляц Банковий: 10
Марії Склодовської-Кюрі вулиця: 18
Висла: 13
аллея Солидарности: 84
улица Адама Мицкевича: 33
```

The most common non-Latin script names are Russian names of streets and places ('аллея Солидарности', 'улица Адама Мицкевича', 'Пляц Банковий', 'Висла'). There is also an Ukrainian name of a street ('Марії Склодовської-Кюрі вулиця') and, surprisingly, a Japanese name of the river Wisła ('ヴィスワ'). These could be changed to Polish names with relative ease, but care should be taken, in case these were included in the map for the convenience of foreign speakers.

## Phase 3: Further exploration of the dataset

### Most common postcodes

```SQL
SELECT value, COUNT(*) AS n
FROM nodes_tags
WHERE key = 'postcode'
GROUP BY value
ORDER BY n
DESC LIMIT 3;
```

```SQL
05-825|10037
05-400|8803
05-303|7690
```

### Most common amenities

```SQL
SELECT value, COUNT(*) AS n
FROM nodes_tags
WHERE key = 'amenity'
GROUP BY value
ORDER BY n DESC
LIMIT 4;
```

```SQL
bench|1642
restaurant|1232
waste_basket|1030
atm|992
```

It seems, that Mazovian district can boast of as many benches as restaurants!

### Places for sport

```SQL
SELECT value, COUNT(*) AS n
FROM nodes_tags
WHERE key = 'sport'
GROUP BY value
ORDER BY n DESC
LIMIT 5;
```

```SQL
swimming|23
table_tennis|19
gymnastics|11
tennis|11
multi|9
```

### Tourist amenities:

```SQL
SELECT value, COUNT(*) AS n
FROM nodes_tags
WHERE key = 'tourism'
GROUP BY value
ORDER BY n DESC
LIMIT 5;
```

```SQL
information|282
artwork|153
hotel|119
attraction|107
museum|80
```

### Architecture

```SQL
SELECT value, COUNT(*) AS n
FROM ways_tags
WHERE key = 'architecture'
GROUP BY value
ORDER BY n DESC;
```

```SQL
baroque|5
classic|1
```

### Advertising

```SQL
SELECT value, COUNT(*) AS n
FROM ways_tags
WHERE key = 'advertising'
GROUP BY value
ORDER BY n DESC;
```

```SQL
billboard|7
column|3
```

### Sources

```SQL
SELECT value, COUNT(*) AS n
FROM ways_tags
WHERE key = 'addr'
GROUP BY value
ORDER BY n DESC
LIMIT 5;
```

```SQL
mapa.um.warszawa.pl|51143
piaseczno.e-mapa.net|6374
grodziskmazowiecki.e-mapa.net|4191
michalowice.e-mapa.net|4017
lomianki.e-mapa.net|3789
```

```SQL
SELECT value, COUNT(*) AS n
FROM ways_tags
WHERE key = 'source'
GROUP BY value
ORDER BY n DESC
LIMIT 5;
```

```SQL
UMiG Piaseczno|5653
Bing|5179
UM Ząbki|3392
UG Izabelin|2164
UG Lesznowola i bing|1920
```


## Phase 4: Ideas for further work

I was greatly impressed with the map of Warsaw. It is obvious that the map was meticulously edited by hundreds of people, and I cannot pinpoint any blunders in it, other than the few issues I mentioned in the map cleaning phase. I undertook the work on the map of Warsaw and its surrounding towns after an unsuccessful attempt at working with the map of Chennai, India, which is another city in which I studies for a longer period of time. There is much qualitative difference between these two datasets. While it might be unjust to compare them, as Chennai is much larger city than Warsaw, the map of Warsaw seems like much more of an accomplished project, with its details carefully arranged.

With that in mind, I see a few areas in which the map could be further developed. I was greatly intrigued discovering the 'architecture' and 'advertising' keys in the dataset, and badly disappointed after discovering, that there is barely any information contained in these keys. It is likely, that individuals living in Warsaw, and interested in researching these subjects (and I know a few concerned with anthropology of a city) could take upon themselves supplementing some of the lacking information.

With regard to architecture, one could wonder whether creating an app testing users on architectonic styles of buildings could be employed in order to provide additional data on the styles in which historic buildings were constructed. With regard to advertising, I believe a more appropriate way to address it would be creation of an internet forum, devoted to the issue of urban advertising. One could anticipate both good sides, and potential problems, that these solutions could bring:

### Benefits of the proposed solutions:

As developing simple mobile applications becomes easier, and more popular among young entrepreneurs, many are looking for a way to provide something new and different. While an app providing a selection of pictures of historical building, and asking its users to identify them---introducing element of gamification into a process which otherwise is considered rather tedious could be exactly the solution which could bring more eager contributors. As I am not a mobile developer myself, I can only assume that the information between such an app, and the OSM, could be shared.

The second idea is that of a forum, in which those interested in urban studies could share information about advertising, murals, and, in more general terms, about urban aesthetics. I think we could assume, that there is a number of people in Warsaw who could be interested in exchanging pictures of objects which they consider particularly interesting, and a forum could impose some rules of standardisation (asking users to provide not only pictures, but also geographical coordinates, or simply marking the object on a map and providing a link). Such a forum could bring not only additional information, but also ideas for further development of a map.

### Possible problems with implementation:

Both of the mentioned ideas can face severe problems with their implementation. With regard to the mobile app, in which users can identify architectonic styles of buildings, the mechanism of the app is a problem. One could assume, that users themselves could upload pictures of buildings, providing some data about them, and then identify the style, with the style which is most 'upvoted' being judged as the default style. While the solution sounds trivial, it is obviously very error-prone. Another problem with the implementation is the exchange of data between the app and the OSM. I believe an exchange of information between API of the mobile app and the OSM is too optimistic scenario to work. Probably the only realistic idea would be to introduce the information provided in the app into the OSM manually, which would be, again, a tedious task.

The mechanism of a forum is, at least in theory, much easier. The problem with this idea is the demand for voluntary administrators of the forum, who would organize the discussion and maintain high standard of conversation. I believe, that exchange of information between forum data and the OSM could be easier than with regard to the app idea.

## Conclusion

The above is an attempt at wrangling the OSM of Warsaw and its surrounding towns. While the code included above was, with the exclusion of passages marked as taken from other sources, written by myself, I would not be able to find out the proper ways to implement it without the sources listed below. One of the most pertinent problems in the dataset was the struggle to properly display Unicode characters. I implemented some of the solutions mentioned in the StackOverflow posts (linked below), and experimented with them, until they worked. This might have caused the code to be much less readable, for which I am sorry.

While I can think of further ways to analyze the data, I think these would demand skills in SQL (or Python) far exceeding mine. These ideas include:

- finding parts of the districts (by postcode?) having the biggest number of amenities, e.g. hotels, churches, restaurants
- assessing, how car-friendly or bike-friendly are certain areas, by counting the number of parking spots and bike lanes
- assessing, which sources contributed to which parts of the map

### Sources used in this project
- [StackOverflow post on converting Unicode](http://stackoverflow.com/questions/13485546/converting-unicode-to-in-python)
- [StackOverflow post on converting XML to CSV](http://stackoverflow.com/questions/31844713/python-convert-xml-to-csv-file)
- [StackOverflow post on checking a string for non-Latin characters](http://stackoverflow.com/questions/3094498/how-can-i-check-if-a-python-unicode-string-contains-non-western-letters)
- [StackOverflow AlKid's solution to the function finding numbers in strings](http://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number)
- [StackOverflow post on changing tag attributes](http://stackoverflow.com/questions/17922056/setting-an-attribute-value-in-xml-file-using-elementtree)
- [StackOverflow post on editing a single field from a CSV file](http://stackoverflow.com/questions/11033590/change-specific-value-in-csv-file-via-python)
- [SQLite documentation on importing CSV files](https://www.sqlite.org/cvstrac/wiki?p=ImportingFiles)
- [ElementTree documentation](https://docs.python.org/2/library/xml.etree.elementtree.html)
- [Python CSV module documentation](https://docs.python.org/2/library/csv.html)
- [Wikipedia article on postal codes in Poland](https://en.wikipedia.org/wiki/Postal_codes_in_Poland)
- [Online search engine for postal codes in Poland](http://kody.jzk.pl/)
- [The excellent sample project, linked up in the course pages, was my constant source of inspiration](https://gist.github.com/carlward/54ec1c91b62a5f911c42#file-sample_project-md)
