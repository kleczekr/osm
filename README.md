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
As I was not acquainted with it (it was different from postal number), I found out it refers to territorial classification of Poland, TERYT. The government statistical portal of Poland contained [an XML file](http://www.stat.gov.pl/broker/access/prefile/listPreFiles.jspa) of all SIMC numbers of Polish cities. In further exploration I will run a function to check if the SIMC numbers are valid, according to the government classification.

