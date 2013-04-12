#!/usr/bin/env python
# Copyright (c) 2013, ASG Consulting
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
#  Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  Neither the name of ASG Consulting nor the names of its contributors
#  may be used to endorse or promote products derived from this software
#  without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import glob
import sys
import re

import texttable

# Define regular expressions for the Apache vhost_combined and combined log
# formats. Other formats will be ignored.
#
# vhost_combined
# %v:%p %h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"
vhc_re = re.compile(r'^(.*:\d+) ([0-9.]+) .* "(.*)" \d+ \d+ "(.*)" "(.*)"$')

# combined
# %h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"
cbn_re = re.compile(r'^([0-9.]+) .* "(.*)" \d+ \d+ "(.*)" "(.*)"$')


def parse_line(line):
    m = vhc_re.match(line)
    if m is not None:
        vhost, host, resource, referer, agent = m.groups()

    m = cbn_re.match(line)
    if m is not None:
        vhost = ''
        host, resource, referer, agent = m.groups()

    if resource != '-':
        resource = resource.split(' ')[1]

    return vhost, host, resource, referer, agent


def parse_log_file(f):
    for line in open(f):
        line = line.strip()
        if line == '':
            continue
        if line.startswith('#'):
            continue

        yield parse_line(line)


def print_table(tname, cname, data):
    t = texttable.TextTable()
    t.header = tname
    t.add_col_names([cname, 'Count'])
    t.add_col_align(['<', '>'])
    for d in sorted(data, key=data.get, reverse=True):
        t.add_row([d, data[d]])

    print t


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'apache_log_parser.py path/to/logs'
        sys.exit(1)

    vhosts = {}

    for f in glob.glob(sys.argv[1] + '/*.log'):
        for vhost, host, res, ref, agent in parse_log_file(f):
            vhosts.setdefault(vhost,
                              {'hosts': {}, 'referers': {},
                               'resources': {}, 'agents': {}})

            data = vhosts[vhost]
            data['hosts'][host] = 1 + data['hosts'].get(host, 0)
            data['agents'][agent] = 1 + data['agents'].get(agent, 0)
            data['resources'][res] = 1 + data['resources'].get(res, 0)
            data['referers'][ref] = 1 + data['referers'].get(ref, 0)

    for vhost in vhosts:
        print '-' * (len(vhost) + 4)
        print '| ' + vhost + ' |'
        print '-' * (len(vhost) + 4)

        print_table('Hosts', 'Host', vhosts[vhost]['hosts'])
        print_table('User Agents', 'User Agent', vhosts[vhost]['agents'])
        print_table('Resources', 'Resource', vhosts[vhost]['resources'])
        print_table('Referers', 'Referer', vhosts[vhost]['referers'])
        print
