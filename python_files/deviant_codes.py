import csv

with open('ways_tags.csv') as f:
    reader = csv.DictReader(f)
    deviant_codes = set()
    for row in reader:
        code = row['value']
        if row['key'] == 'postcode' and int(code[0]) != 0:
            deviant_codes.add(code)
    print deviant_codes

