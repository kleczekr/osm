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

(The above code is basically identical with the one employed in the 'sample submission' file, linked to in the Udacity material. I tried to write different SQL queries, employing the JOIN command, but I came to the conclusion (after several code crashes) that UNION ALL, as explained [e.g. here,](https://www.techonthenet.com/sqlite/union_all.php) is necessary.)

2622

### 20 major contributors:

```SQL
SELECT new.user, COUNT(*) AS n
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) AS new
GROUP BY new.user
ORDER BY n DESC
LIMIT 20;
```
(The above code is, again, not much different from the code given in 'sample submission' file, linked to in the Udacity material. As mentioned above, the UNION ALL operator seems to be necessary, and using it, it is difficult to write the query in radically different manner)

```SQL
rosomak|1221345
kocio|406644
Zibi-importy|185345
Madmaks|142099
balrog-kun-imports|135851
WiktorN-import|132798
Alkomat|132080
lasica1982|122819
RuteX|110259
Javnik|107865
grracjan|104670
NikodemKarolak|96113
Andrzej3345|95485
balrog-kun|83710
masti|83574
Voitcus|79706
lemacik|70806
wajak|68088
michal_f|63063
mpd_cbm|46048
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
LIMIT 20;
```

```SQL
housenumber|401708
street|336792
city|335089
postcode|334573
addr|256926
city:simc|184749
source|171247
street:sym_ul|134332
place|69748
highway|31554
name|27763
ref|14469
amenity|14106
barrier|11497
natural|11399
power|9917
type|8201
emergency|8016
created_by|7621
public_transport|7401
```

```SQL
SELECT key, COUNT(*) AS n
FROM ways_tags
GROUP BY key
ORDER BY n DESC
LIMIT 20;
```

```SQL
building|311286
highway|167694
housenumber|125745
city|124428
street|123576
postcode|118218
addr|104185
city:simc|90981
street:sym_ul|87576
name|65416
landuse|47407
source|40051
surface|36187
maxspeed|23776
oneway|21533
lanes|16069
service|14573
barrier|13549
ref|12865
amenity|12129
```

### Number of cafes, cinemas, and bars

```SQL
sqlite> SELECT value, COUNT(*) AS n FROM nodes_tags WHERE value = 'cafe' GROUP BY value; 
```
487

```SQL
sqlite> SELECT value, COUNT(*) AS n FROM nodes_tags WHERE value = 'cinema' GROUP BY value;
```
36

```SQL
sqlite> SELECT value, COUNT(*) AS n FROM nodes_tags WHERE value = 'bar' GROUP BY value;
```
138


## Phase 2: auditing and cleaning the dataset

### The SIMC number

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
import sys
reload(sys)
sys.setdefaultencoding('utf-8') # The three above lines are included to properly display Unicode chars

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

### Street names

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

import sys
reload(sys)
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
```

The loop at the end is included in order to display the Unicode characters properly. The output is as follows:

```python
Powstańców Warszawy 17: 1
Karczewska 14/16: 1
Ireny Kosmowskiej - Grodzieńska 21/29: 1
Powstańców Warszawy 19: 1
```

And indicates, that each of the problematic names occurs only once in the entire map. As the above names do not denote street names, but entire addresses, they can be removed from the map.


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
set(['96-314', '96-315', '96-316', '96-300', '91-065', '26-914', '96-313', '96-102', '96-515', '96-516', '96-111', '96-321', '96-320', '96-330', '96-325', '96-323'])
```

After a while of searching for details online, I established, that postcodes beginning with '96' also belong to Masovian district. There are two other types of codes left in the set: '26-914' and '91-065'. The first one, '26-914', is also located in Masovian district. The second one, '91-065', is located in the neighbouring Lodz district, and should be corrected.

### Non-Latin characters in the map

As I mentioned, I discovered, that there are fields in the data containing non-Latin characters, predominantly Russian. As I have been looking for ways of finding these fields, I came upon a [StackOverflow post](http://stackoverflow.com/questions/3094498/how-can-i-check-if-a-python-unicode-string-contains-non-western-letters) containing code for checking string for non-Latin characters. Below is the code I adapted for checking the map data:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unicodedata as ud
import csv
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

latin_letters= {}

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
    not_romans = set()
    count = 0
    for row in reader:
        for field in row.values():
            if not only_roman_chars(unicode(field, 'utf-8')):
                not_romans.add(field)
    for stuff in not_romans:
        print unicode(stuff, 'utf-8')
```

As the output indicates, majority of the fields writen in non-Latin scripts are written in either Russian, or Ukrainian:

```python
ヴィスワ
Президентский дворец в Варшаве
Міст Понятовського
Варшавская школа экономики
Посольство України
ארקדיה
Варшавський фінансовий центр
Заходні Буг
Пляц Банковий
Варшавська політехніка
Колонна короля Сигизмунда в Варшаве
جامعة وارسو
주 폴란드 대한민국 대사관
11-го Листопада
Повонзківський цвинтар
Посольство России в Польше
Марії Склодовської-Кюрі вулиця
Висла
Музей охоты и верховой езды
Статуя Сиренки
Варшавский университет
Бельведерский дворец в Варшаве
Посольство Республики Узбекистан
Юля 8560
Новогеоргиевская крепость
Церковь Успения Божией Матери и Святого Иосифа
аллея Солидарности
памятник Яну Килиницкому
Костел святого Мартина
Франкліна Рузвельта
קניון עודפים( אוטובוס 517 מתחנה מרכזית )
стоянка
улица Адама Мицкевича
ポーランド日本情報工科大学
ночлег
Международный Аэропорт имени Фредерика Шопена
워크리브트레블 민박
Алея «Солідарності»
Дорина
Тадеуша Сиґетинського
Центральный Железнодорожный Вокзал
在ポーランド日本国大使館
Західний Буг
Центральний статистичний офіс Польщі
Западный Буг
Варшавский политехнический институт
Нараў
розборка пежо
Палац Красінських
Вісла
Кафедральний собор Івана Хрестителя
Європейська площа
Варшавське наукове товариство
Варшава АС Восточная
Буг
Піонерська вулиця
נמל התעופה ורשה פרדריק שופן
부크
```
This might not be a problem, since the list is not very long. We can take a look at how often these names are used. The following prints the names which occur more than five times:

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
    for item in not_romans.keys():
        if not_romans[item] > 5:
            print item + ': ' + str(not_romans[item])
```

The above code might look a little strange, as I needed to use a workaround in order to display unicode strings properly. The output is as follows:

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
SELECT value, COUNT(*) AS n FROM nodes_tags WHERE key = 'postcode' GROUP BY value ORDER BY n DESC LIMIT 3;
```

```SQL
05-825|10037
05-400|8803
05-303|7690
```

### Most common amenities

```SQL
SELECT value, COUNT(*) AS n FROM nodes_tags WHERE key = 'amenity' GROUP BY value ORDER BY n DESC LIMIT 4;
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
SELECT value, COUNT(*) AS n FROM nodes_tags WHERE key = 'sport' GROUP BY value ORDER BY n DESC;
```

```SQL
swimming|23
table_tennis|19
gymnastics|11
tennis|11
multi|9
skateboard|9
equestrian|8
basketball|7
soccer|7
chess|4
fitness|4
10pin|3
canoe|2
climbing|2
wakeboard|2
9pin|1
Siłownia|1
billard|1
bowling|1
bungee|1
dance|1
diving;scubadiving|1
fighting|1
gymnastics;martial_arts|1
judo|1
model_aerodrome|1
paintball|1
rc_plane|1
sailing|1
scuba_diving|1
shooting|1
ski|1
skiing|1
surfing|1
volleyball|1
```

### Tourist amenities:

```SQL
SELECT value, COUNT(*) AS n FROM nodes_tags  WHERE key = 'tourism' GROUP BY value ORDER BY n DESC;
```

```SQL
information|282
artwork|153
hotel|119
attraction|107
museum|80
viewpoint|50
picnic_site|46
hostel|38
chalet|35
guest_house|26
motel|12
camp_site|6
apartment|3
caravan_site|2
gallery|2
meeting_point|1
office|1
zoo|1
```

### Architecture

```SQL
SELECT value, COUNT(*) AS n FROM ways_tags WHERE key = 'architecture' GROUP BY value ORDER BY n DESC;
```

```SQL
baroque|5
classic|1
```

### Advertising

```SQL
SELECT value, COUNT(*) AS n FROM ways_tags WHERE key = 'advertising' GROUP BY value ORDER BY n DESC;
```

```SQL
billboard|7
column|3
```

### Sources

```SQL
SELECT value, COUNT(*) AS n FROM ways_tags WHERE key = 'addr' GROUP BY value ORDER BY n DESC LIMIT 5;
```

```SQL
mapa.um.warszawa.pl|51143
piaseczno.e-mapa.net|6374
grodziskmazowiecki.e-mapa.net|4191
michalowice.e-mapa.net|4017
lomianki.e-mapa.net|3789
```

```SQL
SELECT value, COUNT(*) AS n FROM ways_tags WHERE key = 'source' GROUP BY value ORDER BY n DESC LIMIT 5;
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
- [SQLite documentation on importing CSV files](https://www.sqlite.org/cvstrac/wiki?p=ImportingFiles)
- [ElementTree documentation](https://docs.python.org/2/library/xml.etree.elementtree.html)
- [Python CSV module documentation](https://docs.python.org/2/library/csv.html)
- [Wikipedia article on postal codes in Poland](https://en.wikipedia.org/wiki/Postal_codes_in_Poland)
- [Online search engine for postal codes in Poland](http://kody.jzk.pl/)
- [The excellent sample project, linked up in the course pages, was my constant source of inspiration](https://gist.github.com/carlward/54ec1c91b62a5f911c42#file-sample_project-md)
