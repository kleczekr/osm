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