import csv

def numbers(s):
    return any(i.isdigit() for i in s)

with open('ways_tags.csv') as f:
    reader = csv.DictReader(f)
    new_set = set()
    for row in reader:
        if row['key'] == 'street' and numbers(row['value']):
            new_set.add(row['value'])
    for value in new_set:
        print unicode(value, 'utf-8').encode('utf-8')

