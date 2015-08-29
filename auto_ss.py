#! /usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import hashlib
import argparse
import time
import subprocess
import signal
import contextlib
from functools import wraps

import requests
import requesocks
from bs4 import BeautifulSoup


# ss-link
login_url = 'https://www.ss-link.com/login'
free_ss_account_url = 'https://www.ss-link.com/my/free'

# ss-local
ss_local_cmd_tpl = \
    ('sslocal -s {server_address} -p {server_port} -l'
     ' {local_port} -k {server_password} -m'
     ' {server_encrypt_method}')


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


class ShadowsocksRuntimeError(RuntimeError):
    pass


class TimeoutException(Exception):
    pass


def _grab_ss_link_free_accounts(email, password):
    payload = {
        'email': email,
        'password': hashlib.md5(password).hexdigest(),
        'redirect': free_ss_account_url,
    }
    resp = requests.post(login_url, data=payload, headers=headers,
                         verify=True)
    if resp.status_code != requests.status_codes.codes.ok:
        resp.raise_for_status()

    if 'E-Mail is not exist' in resp.text or \
            'password is incorrect' in resp.text:
        raise AccountInvalidException('ss-link account invalid')

    soup = BeautifulSoup(resp.text, 'html.parser')

    free_accounts = []
    for ss_account_record_node in soup.table.tbody.find_all('tr'):
        sub_nodes = ss_account_record_node.find_all('td')
        server_address = sub_nodes[1].string.strip()
        server_port = int(sub_nodes[2].string.strip())
        server_password = sub_nodes[3].string.strip()
        server_encrypt_method = sub_nodes[4].string.strip()

        free_accounts.append(
            {
                'server_address': server_address,
                'server_port': server_port,
                'server_password': server_password,
                'server_encrypt_method': server_encrypt_method,
            }
        )
    return free_accounts


@contextlib.contextmanager
def func_timeout(seconds=10, error_message='Timeout'):
    def _handle_timeout(signum, frame):
        raise TimeoutException(error_message)

    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.alarm(seconds)
    yield
    signal.alarm(0)


def ss_local_deco(func, *d_args, **d_kwargs):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ss_local_cmd = \
            ss_local_cmd_tpl.format(
                **d_kwargs
            )
        try:
            p = subprocess.Popen(
                "exec " + ss_local_cmd, shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

            try:
                # fix p.stdout.read block
                with func_timeout(1):
                    stderr = p.stdout.read()
                    if stderr:
                        raise ShadowsocksRuntimeError(stderr)
            except TimeoutException:
                pass

            kwargs.update({'local_port': d_kwargs['local_port']})
            speed = func(*args, **kwargs)
        except TimeoutException:
            speed = 0
        else:
            p.kill()
            return speed or 0
    return wrapper


def ss_speed_test(*args, **kwargs):
    try:
        local_port = kwargs.get('local_port')
        socks5_proxies = {
            'http': 'socks5://127.0.0.1:{}'.format(local_port),
            'https': 'socks5://127.0.0.1:{}'.format(local_port)
        }
        start = time.time()
        resp = requesocks.get('https://www.google.com.hk',
                              proxies=socks5_proxies,
                              timeout=kwargs.get('timeout', 5))
        cost = time.time() - start
        if resp.status_code == requesocks.status_codes.codes.ok:
            return int(int(len(resp.text)) / 1024 / cost)
    except Exception:
        return 0


def test_ss_accounts_speed(free_ss_accounts, local_port, timeout):
    print '\n{:#^72}'.format(' Connection Test ')

    free_ss_speeds = []
    for ss_account in free_ss_accounts:
        try:
            speed = ss_local_deco(ss_speed_test, local_port=local_port,
                                  **ss_account)(timeout=timeout)
        except ShadowsocksRuntimeError as e:
            print e
            sys.exit(1)

        free_ss_speeds.append((ss_account, speed))
        print '{:<30}{:>42}'.format(
            ss_account['server_address'],
            'speed is: {}kb/s'.format(speed) if speed else 'connection timeout'
        )
    return free_ss_speeds


def get_free_ss_accounts(args):
    free_ss_accounts = _grab_ss_link_free_accounts(args.email, args.password)
    local_port = getattr(args, 'local_port', 1800)
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
        test_ss_accounts_speed(free_ss_accounts, local_port, args.timeout)
    elif args.mode == 'run':
        ss_speeds = test_ss_accounts_speed(free_ss_accounts,
                                           local_port, args.timeout)
        ss_speeds = \
            sorted(ss_speeds, key=lambda x: x[1], reverse=True)
        if ss_speeds[0][1] != 0:
            ss_account = ss_speeds[0][0]
            print 'sslocal running at port {}'.format(local_port)
            p = subprocess.Popen(
                ss_local_cmd_tpl.format(local_port=local_port,
                                        **ss_speeds[0][0]),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            while True:
                print p.stdout.readline()


def main():
    parser = argparse.ArgumentParser(
        description='Auto acquire ss-link free shadowsocks accounts.')
    parser.add_argument('email', help='ss-link email')
    parser.add_argument('password', help='ss-link password')
    parser.add_argument('-m', '--mode', default='avaiable',
                        help=('run mode, deault `avaiable`. '
                              'if mode is `speed`, '
                              'will test network connection')
                        )
    parser.add_argument('-t', '--timeout',
                        help='connection timeout in seconds, default 10',
                        default=10, type=int)
    parser.add_argument('-p', '--local_port',
                        help='sslocal local_port, default 1080',
                        default=1080, type=int)

    args = parser.parse_args()
    try:
        get_free_ss_accounts(args)
    except AccountInvalidException:
        print 'invalid ss-link account'
    except (KeyboardInterrupt):
        print '\nUser Stopped\n'


if __name__ == '__main__':
    main()
