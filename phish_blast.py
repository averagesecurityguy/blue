import requests
import random

first_file = 'firstnames.txt'
last_file = 'lastnames.txt'
domain_file = 'domains.txt'
pass_file = 'passwords.txt'
login_url = 'http://jts-bd.org/admin/include/login.php'
user_field = 'Email'
pass_field = 'emailpassword'

def load_file(filename):
    items = []

    with open(filename) as f:
        for line in f:
            items.append(line.rstrip())

    return items


def generate_username(first, last):
    s = random.choice([1, 2, 3, 4])

    if s == 1:
        return '{0}.{1}'.format(first, last)
    if s == 2:
        return '{0}{1}'.format(first[0], last)
    if s == 3:
        return '{0}{1}'.format(first, last[0])
    if s == 4:
        return '{0}.{1}'.format(last, first)


def send_creds(email, pwd):
    print('Sending {0}/{1} to {2}.'.format(email, pwd, login_url))
    creds = {user_field: email, pass_field: pwd}
    try:
        requests.post(login_url, data=creds, allow_redirects=False)

    except Exception as e:
        print('Request failed: {0}'.format(str(e)))


if __name__ == '__main__':
    firsts = load_file(first_file)
    lasts = load_file(last_file)
    doms = load_file(domain_file)
    pwds = load_file(pass_file)

    while True:
        first = random.choice(firsts)
        last = random.choice(lasts)
        dom = random.choice(doms)
        pwd = random.choice(pwds)
        email = '{0}@{1}'.format(generate_username(first, last), dom)

        send_creds(email, pwd)
