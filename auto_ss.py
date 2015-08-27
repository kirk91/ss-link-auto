#! /usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import argparse
import json
import time
import inspect
import subprocess
import signal
import contextlib

import requests
import requesocks
from bs4 import BeautifulSoup


# ss-link
login_url = 'https://www.ss-link.com/login'
free_ss_account_url = 'https://www.ss-link.com/my/free'

headers = {
    'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,'
               'image/webp,*/*;q=0.8'),
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/44.0.2403.157 Safari/537.36'),
}


class AccountInvalidException(Exception):
    pass


def _grab_ss_link_free_accounts(email, password):
    payload = {
        'email': email,
        'password': hashlib.md5(password).hexdigest(),
        'redirect': free_ss_account_url,
    }
    resp = requests.post(login_url, data=payload, headers=headers)
    if resp.status_code != requests.status_codes.codes.ok:
        resp.raise_for_status()

    if 'E-Mail is not exist' in resp.text or \
        'password is incorrect' in resp.text:
        raise AccountInvalidException('ss-link account invalid')

    soup = BeautifulSoup(resp.text, 'html.parser')

    free_accounts = []
    for ss_account_record_node in soup.table.tbody.find_all('tr'):
        sub_nodes = ss_account_record_node.find_all('td')
        route = u'{}'.format(sub_nodes[0].string.strip())
        server_address = sub_nodes[1].string.strip()
        server_port = int(sub_nodes[2].string.strip())
        server_password = sub_nodes[3].string.strip()
        server_encrypt_method = sub_nodes[4].string.strip()

        free_accounts.append(
            {
                'route': route,
                'server_address': server_address,
                'server_port': server_port,
                'server_password': server_password,
                'server_encrypt_method': server_encrypt_method,
            }
        )
    return free_accounts


@contextlib.contextmanager
def timeout(seconds=10, error_message='Timeout'):
    def _handle_timeout(signum, frame):
        return error_message

    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.alarm(seconds)
    yield
    signal.alarm(0)


def ss_speed_test(**kwargs):
    local_port = kwargs.get('local_port', 1801)
    ss_local_cmd = 'sslocal -s {} -p {} -l {} -k {} -m {}'.format(
        kwargs['server_address'], kwargs['server_port'],
        local_port, kwargs['server_password'],
        kwargs['server_encrypt_method']
    )

    try:
        p = subprocess.Popen(
            "exec " + ss_local_cmd, shell=True, stdout=open('/dev/null', 'w'),
            stderr=subprocess.STDOUT
        )
        time.sleep(1)

        socks5_proxies = {
            'http': 'socks5://127.0.0.1:{}'.format(local_port),
            'https': 'socks5://127.0.0.1:{}'.format(local_port)
        }
        start = time.time()
        resp = requesocks.get('https://www.google.com.hk',
                              proxies=socks5_proxies, timeout=5)
        cost = time.time() - start
        if resp.status_code == requesocks.status_codes.codes.ok:
            return '{}kb/s'.format(int(len(resp.text)/1024/cost))
    except Exception as e:
        return 'Timeout'
    finally:
        p.kill()


def get_free_ss_accounts(args):
    free_ss_accounts = _grab_ss_link_free_accounts(args.email, args.password)

    print("{:#^72}".format(
        ' {} Shadowsocks Accounts '.format(time.strftime('%Y-%m-%d %H:%M:%S'))
         ))
    print('{:<20} {:<12}   {:<20} {}'.format(
        'server_address', 'server_port', 'server_password', 'encrypt_method'
    ))
    print '=' * 72
    for ss_account in free_ss_accounts:
        print ('{server_address:<20} {server_port:^12} {server_password:^20} '
               '{server_encrypt_method:^18}').format(**ss_account)

    if args.mode == 'speed':
        print('\n{:#^72}'.format(' Connection Test '))
        for ss_account in free_ss_accounts:
            print(u'{:<30}'.format(
                ss_account['server_address'])),
            with timeout(args.timeout):
                speed = ss_speed_test(**ss_account)
                if speed != 'Timeout':
                    print('{:>42}'.format('speed is: ' + speed))
                else:
                    print('{:>42}'.format(speed))
    else:
        pass

def main():
    parser = argparse.ArgumentParser(
        description='Auto acquire ss-link free shadowsocks accounts.')
    parser.add_argument('email', help='ss-link email')
    parser.add_argument('password', help='ss-link password')
    parser.add_argument('--mode', default='avaiable',
                        help=('run mode, deault `avaiable`. '
                              'if mode is `speed`, will test network connection')
                             )
    parser.add_argument('--timeout',
                        help='connection timeout in seconds, default 10',
                        default=10, type=int)

    args = parser.parse_args()
    try:
        get_free_ss_accounts(args)
    except (KeyboardInterrupt, SystemExit):
        print '\nUser Stopped\n'
    except AccountInvalidException as e:
        print e


if __name__ == '__main__':
    main()
