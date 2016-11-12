# Data Wrangling with Python and SQL
### openStreetMap project

The following is an attempt at wrangling the Open Street Map of Warsaw, Poland, as I lived there during my study years, and I know it rather well.

The data was downloaded from the website of the [Map Zen](https://mapzen.com/data/metro-extracts/metro/warsaw_poland/) project.

## Introductory exploration of data

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



As I explored street names, I was quite surprised to find no major mistakes or abbreviations. It might have been caused by the convention used in Polish edition of the OSM, where there is no equivalent of the 'Street' noun used by the street names (in Polish, it is put before the name of the street, and conventionally abbreviated to 'Ul.').



## Sources used in this project
- [StackOverflow post on converting Unicode](http://stackoverflow.com/questions/13485546/converting-unicode-to-in-python)
- [StackOverflow post on converting XML to CSV](http://stackoverflow.com/questions/31844713/python-convert-xml-to-csv-file)
- [SQLite documentation on importing CSV files](https://www.sqlite.org/cvstrac/wiki?p=ImportingFiles)
- [ElementTree documentation](https://docs.python.org/2/library/xml.etree.elementtree.html)
- [Python CSV module documentation](https://docs.python.org/2/library/csv.html)
