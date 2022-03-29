import ctypes
import os
import sys

from variables import DNS_NAME, DNS_IP


def register_domain_name():
    os_name = os.name
    if os_name == 'nt':
        path = os.environ['SYSTEMROOT'] + '\System32\drivers\etc\hosts'
    elif os_name == 'posix':
        path = '/etc/hosts'

    run_admin = True
    with open(path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            if line[:-1] == DNS_IP + ' ' + DNS_NAME:
                run_admin = False

    if run_admin:
        if os_name == 'nt' and not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, ' '.join(sys.argv), None, 1)
            exit(0)
        elif os_name == 'posix' and os.getuid() != 0:
            print('Please exececute command: sudo venv/bin/python3.7 register_domain_name.py')
            exit(0)
        else:
            with open(path, 'a') as f:
                f.write('\n' + DNS_IP + ' ' + DNS_NAME + '\n')


if __name__ == '__main__':
    register_domain_name()
