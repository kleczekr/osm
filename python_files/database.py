import sqlite3
import csv
from pprint import pprint

'''
Very little of the present code was my own making. I re-used the code presented by Myles 
on the forum: https://discussions.udacity.com/t/creating-db-file-from-csv-files-with-non-ascii-unicode-characters/174958/7
'''

sqlite_file = 'mydb.db' # sqlite database file

# Connect to the database
conn = sqlite3.connect(sqlite_file)

# Get a cursor object
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS nodes')
cur.execute('DROP TABLE IF EXISTS nodes_tags')
cur.execute('DROP TABLE IF EXISTS ways')
cur.execute('DROP TABLE IF EXISTS ways_tags')
cur.execute('DROP TABLE IF EXISTS ways_nodes')
cur.execute('DROP TABLE IF EXISTS simc')

conn.commit()

cur.execute('''
    CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
    );
''')
cur.execute('''
    CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
    );
''')
cur.execute('''
    CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
    );
''')
cur.execute('''
    CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
    );
''')
cur.execute('''
    CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
    );
''')
cur.execute('''
    CREATE TABLE simc (
    name TEXT NOT NULL,
    sym INTEGER NOT NULL,
    sympod INTEGER NOT NULL
    );
    ''')

# Commit the changes
conn.commit()

'''
In the following, I had to use the .decode("utf-8") clause to avoid errors with Unicode strings
(not my original idea, mentioned in the forum thread:
https://discussions.udacity.com/t/creating-db-file-from-csv-files-with-non-ascii-unicode-characters/174958/7)
'''

# Read in the csvs as dictionaries, format as list of tuples
with open('nodes_tags.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"), i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in dr]

#insert the data
cur.executemany("INSERT INTO nodes_tags(id, key, value, type) VALUES (?, ?, ?, ?);", to_db)

with open('ways_tags.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"), i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO ways_tags(id, key, value, type) VALUES (?, ?, ?, ?);", to_db)

with open('nodes.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode("utf-8"), i['lat'].decode("utf-8"), i['lon'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)

with open('ways.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)

with open('ways_nodes.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode("utf-8"), i['node_id'].decode("utf-8"), i['position'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db)

with open('simc.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['name'].decode("utf-8"), i['sym'].decode("utf-8"), i['sympod'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO simc(name, sym, sympod) VALUES (?, ?, ?);", to_db)

# Commit the changes
conn.commit()


cur.execute('SELECT * FROM nodes_tags')
all_rows = cur.fetchall()
print('1):')
print all_rows

conn.close()





