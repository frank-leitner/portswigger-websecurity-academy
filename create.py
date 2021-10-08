#!/usr/bin/env python3
import argparse
from bs4 import BeautifulSoup
import fileinput
import logging
import os
import requests
from shutil import copy
import sys


def process_arguments():
    desc = ('Create a skeleton for a new PortSwigger Academy writeup\n'
            'It will be create as sub-directory in the current working directory.\n')
    parser = argparse.ArgumentParser(
        description=desc, formatter_class=argparse.RawTextHelpFormatter)

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument('-u', '--url', required=True,
                          help='URL of the lab')

    optional.add_argument('-d', '--debug', action='store_true',
                          help='Even more verbose output')
    args = parser.parse_args()

    log_format = '[%(levelname)8s] %(message)s'
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    return args


def check_config(args):
    return True


def get_details(url):
    r = requests.get(url)
    if not r.status_code == 200:
        logging.error(f'Failed to load URL {url}')
        return False
    soup = BeautifulSoup(r.text, 'html.parser')

    d = {}
    try:
        d['title'] = soup.find('h1').text.strip()
        d['url'] = url
        d['level'] = soup.find('div', {'class': 'widget-container-labelevel'}).span.text.strip()
    except AttributeError:
        logging.error(f'Failed to extract some info from page')
        return False

    return d


def create_skeleton(details):
    template_dir = f'{os.path.dirname(os.path.realpath(__file__))}/.templates'
    target_dir = os.path.join(os.getcwd(), details['title'][5:].replace(' ', '_'))
    os.mkdir(target_dir)

    for file in os.listdir(template_dir):
        if os.path.isfile(f'{template_dir}/{file}'):
            copy(f'{template_dir}/{file}', target_dir)

            for line in fileinput.input(f'{target_dir}/{file}', inplace=1):
                line = line.replace('<LAB_NAME>', details['title'])
                line = line.replace('<LAB_LINK>', details['url'])
                line = line.replace('<LAB_LEVEL>', details['level'])
                print(line, end='')


def main():
    args = process_arguments()
    if not check_config(args):
        logging.error(f'Invalid state in arguments: {args}')
        sys.exit(-1)

    details = get_details(args.url)
    if not details:
        sys.exit(-2)

    create_skeleton(details)


if __name__ == "__main__":
    main()
