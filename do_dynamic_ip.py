#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2015, LCI Technology Group, LLC
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   Neither the name of LCI Technology Group, LLC nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
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

import requests
import json
import re
import random

"""
Use the DigitalOcean DNS system to maintain a DNS entry for a dynamic IP
address. Before using this script you will need to create a DigitalOcean
account, an API key (https://www.digitalocean.com/help/api/), and a domain.

Enter the domain name, the name you want associated with the IP address, and
the API key for your account. Other than that, no other changes should be made
to the script.
"""
domain = 'mydomain.com'
name = 'home'
api_key = ''


# Do not edit anything below this line.
dyndns_re = re.compile(r'<body>Current IP Address: ([0-9.]+)</body>')
ifconfig_re = re.compile(r'<strong id="ip_address">([0-9.]+)</strong>')


def send(method, endpoint, data=None):
    """
    Send an API request.

    Send the any provided data to the API endpoint using the specified method.
    Process the API response and print any error messages.
    """
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {0}'.format(api_key)}

    url = 'https://api.digitalocean.com/v2/{0}'.format(endpoint)
    resp = None

    if method in ['POST', 'DELETE', 'PUT']:
        data = json.dumps(data)

    if method == 'POST':
        resp = requests.post(url, headers=headers, data=data)
    elif method == 'DELETE':
        resp = requests.delete(url, headers=headers, data=data)
    elif method == 'PUT':
        resp = requests.put(url, headers=headers, data=data)
    else:
        resp = requests.get(url, headers=headers, params=data)

    if resp.content != b'':
        data = resp.json()

    if resp.status_code in range(400, 499):
        print('[-] Request Error: {0}'.format(data['message']))
        return None

    if resp.status_code in range(500, 599):
        print('[-] Server Error: {0}'.format(data['message']))
        return None

    return data


def get(url):
    """
    GET the specified URL.
    """
    try:
        resp = requests.get(url, timeout=10)
        return resp.content.strip().decode()
    except:
        return None


def get_new_ip():
    """
    Determine the current external IP address using one of five options.
    """
    ip = None
    choice = random.choice(['ipinfo', 'dyndns', 'ipecho', 'ifconfig', 'icanhazip'])

    print('[*] Get current external IP address with {0}.'.format(choice))

    if choice == 'ipinfo':
        ip = get('http://ipinfo.io/ip')

    elif choice == 'dyndns':
        m = dyndns_re.search(get('http://checkip.dyndns.org'))
        if m is not None:
            ip = m.group(1)

    elif choice == 'ipecho':
        ip = get('http://ipecho.net/plain')

    elif choice == 'ifconfig':
        m = ifconfig_re.search(get('http://ifconfig.me'))
        if m is not None:
            ip = m.group(1)

    elif choice == 'icanhazip':
        ip = get('http://icanhazip.com')

    else:
        pass

    print(ip)
    return ip


def get_current_record(name, domain):
    """
    Get the id for the current A record.
    """
    print('[*] Get current DNS record for {0}.{1}.'.format(name, domain))
    resp = send('GET', 'domains/{0}/records'.format(domain))

    for record in resp['domain_records']:
        if record['name'] == name:
            print('[+] Found DNS record.')
            return record['id'], record['data']

    print('[-] Could not find DNS record.')
    return None, None


def create_A_record(name, domain, ip):
    """
    Create a new A record for name.domain and set it to the specified IP
    address.
    """
    print('[*] Creating DNS record for {0}.{1} with IP {2}'.format(name, domain, ip))
    record = {'type': 'A',
              'name': name,
              'data': ip,
              'priority': None,
              'port': None,
              'weight': None}

    send('POST', 'domains/{0}/records'.format(domain), record)


def update_A_record(name, domain, rid, ip):
    """
    Update an A record for domain and set it to the specified IP address.
    """
    print('[*] Updating DNS record for {0}.{1} with IP {2}'.format(name, domain, ip))
    record = {'data': ip}

    send('PUT', 'domains/{0}/records/{1}'.format(domain, rid), record)


if __name__ == '__main__':
    # Get the current record if it exists.
    rid, old_ip = get_current_record(name, domain)

    # Get the current external IP address.
    new_ip = get_new_ip()
    while new_ip is None:
        new_ip = get_new_ip()

    # If the record doesn't exist then create it.
    if rid is None:
        create_A_record(name, domain, new_ip)

    # If the IP address has changed then update the record, otherwise don't.
    if (old_ip is not None) and (new_ip != old_ip):
        update_A_record(name, domain, rid, new_ip)
    else:
        print('[+] External IP address has not changed.')
