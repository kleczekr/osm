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

