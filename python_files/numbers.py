import csv

def numbers(s):
    return any(i.isdigit() for i in s)

with open('ways_tags.csv') as f:
    reader = csv.DictReader(f)
    new_set = set()
    for row in reader:
        if row['key'] == 'street' and numbers(row['value']):
            new_set.add(row['value'])
    # The set cannot simply be printed, as the Unicode characters would not be displayed properly.
    # The following loop is created specifically to display the names nicely, with Unicode characters and all.
    for value in new_set:
        print unicode(value, 'utf-8').encode('utf-8')

