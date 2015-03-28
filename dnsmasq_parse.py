import datetime
import sqlite3
import time
import sys
import re

#-----------------------------------------------------------------------------
# Compiled Regular Expressions
#-----------------------------------------------------------------------------
q_re = re.compile(r'(.*) dnsmasq\[\d+\]: query\[(.*)\] (.*) from (.*)')
f_re = re.compile(r'(.*) dnsmasq\[\d+\]: forwarded (.*) to (.*)')
r_re = re.compile(r'(.*) dnsmasq\[\d+\]: (reply|cached) (.*) is (.*)')


#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------
def create_tables():
    qt = '''
    CREATE TABLE IF NOT EXISTS queries (
        id integer primary key autoincrement,
        source text,
        query_type text,
        name text,
        ts datetime
    )
    '''
    c.execute(qt)
    conn.commit()

    ft = '''
    CREATE TABLE IF NOT EXISTS forwards (
        id integer primary key autoincrement,
        resolver text,
        name text,
        ts datetime
    )
    '''
    c.execute(ft)
    conn.commit()  

    rt = '''
    CREATE TABLE IF NOT EXISTS replies (
        id integer primary key autoincrement,
        ip text,
        reply_type text,
        name text,
        ts datetime
    )
    '''
    c.execute(rt)
    conn.commit()


def convert_date(ds):
    y = str(datetime.datetime.now().year)
    ltime = time.strptime('{0} {1}'.format(y, ds), '%Y %b %d %H:%M:%S')

    return time.strftime('%Y-%m-%d %H:%M:%S', ltime)


def parse_query(query):
    m = q_re.match(query)
    if m is not None:
        counts['qc'] += 1
        add_query(m.group(4), m.group(2), m.group(3), m.group(1))


def parse_forward(query):
    m = f_re.match(query)
    if m is not None:
        counts['fc'] += 1
        add_forward(m.group(3), m.group(2), m.group(1))


def parse_reply(query):
    m = r_re.match(query)
    if m is not None:
        counts['rc'] += 1
        add_reply(m.group(4), m.group(2), m.group(3), m.group(1))


def add_query(source, qtype, name, ts):
    sql = "INSERT INTO queries (source, query_type, name, ts) VALUES(?,?,?,?)"
    c.execute(sql, (source, qtype, name, convert_date(ts)))


def add_forward(resolver, name, ts):
    sql = "INSERT INTO forwards (resolver, name, ts) VALUES(?,?,?)"
    c.execute(sql, (resolver, name, convert_date(ts)))


def add_reply(ip, rtype, name, ts):
    sql = "INSERT INTO replies (ip, reply_type, name, ts) VALUES(?,?,?,?)"
    c.execute(sql, (ip, rtype, name, convert_date(ts)))


#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if len(sys.argv) != 2:
    print 'Usage: dnsmasq_parse.py logfile'
    sys.exit()

logfile = sys.argv[1]

counts = {'lc': 0, 'qc': 0, 'fc': 0, 'rc': 0, 'bc':0}

# Create the SQLite connection
conn = sqlite3.connect('dnsmasq.sqlite')
c = conn.cursor()

create_tables()

# Parse the log file.
for line in open(logfile):
    line = line.rstrip()
    counts['lc'] += 1

    if (counts['lc'] % 10000) == 0:
        print 'Processed {0} lines.'.format(counts['lc'])
        conn.commit()

    if ': query[' in line:
        parse_query(line)

    elif ': forwarded ' in line:
        parse_forward(line)

    elif (': reply ' in line) or (': cached ' in line):
        parse_reply(line)

    else:
        counts['bc'] += 1

print 'Imported {0} log entries.'.format(counts['lc'] - counts['bc'])
print '{0} queries, {1} forwards, and {2} replies.'.format(counts['qc'],
                                                           counts['fc'],
                                                           counts['rc'])
