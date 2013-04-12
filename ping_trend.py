import sqlite3
import os
import re
import time

ping_re = re.compile('\d+ bytes from \d+.\d+.\d+.\d+:', re.I)


def update_db(ip, status, timestamp):
    valstr = "'{0}','{1}','{2}'".format(ip, status, timestamp)
    c.execute("INSERT INTO pings VALUES(" + valstr + ")")
    conn.commit()

# Create the SQLite connection
conn = sqlite3.connect('ping_trend.db')
c = conn.cursor()

# Create the pings table if it does not exist.
c.execute("CREATE TABLE IF NOT EXISTS pings (ip text, status text, time integer)")

# Read through a file of IP addresses and ping each one. Then update the
# database with the status.
for line in open('iplist.txt', 'r'):
    line = line.strip()
    if line == '':
        continue
    if line.startswith('#'):
        continue
    output = os.popen('ping -c 1 ' + line).read()
    m = ping_re.search(output)
    if m is not None:
        update_db(line, 'UP', int(time.time()))
    else:
        update_db(line, 'DOWN', int(time.time()))

# Close the DB connection
conn.commit()
conn.close()
