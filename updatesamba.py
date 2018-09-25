#!/usr/bin/python
# coding=utf-8

import paramiko
import configparser
import datetime
from time import sleep
import sys


def ssh_chmod(host, port, username, password, remote_file, userid, usergroup):
    '''
    Mova smb.conf to /etc/samba/smb.conf and change the owner to root:root,
    and restart samba service.

    @ param host: <str> Remote host's IP.
    @ param port: <int> Remote host's port for sftp
    @ param username: <str> Remote host's login username for ssh.
    @ param password: <str> Remote host's login password for ssh.
    @ param remote: <str> Remote host upload folder.
    @ param userid: <str> The file user to be changed.
    @ param usergroup: <str> The file group to be changed.
    '''
    paramiko.util.log_to_file('samba_ssh.log')

    ssh = paramiko.SSHClient()
    # Allow connections to hosts that are not in the know_hosts.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port=port, username=username, password=password)

    try:
        '''
        The -S flag tells sudu to expect the password to come from stdin
        The -p '' flag tells sudo to use '' or the empty string as the prompt
        for the password.
        '''
        stdin, stdout, stderr = ssh.exec_command(
            "sudo -S -p '' mv %s /etc/samba/smb.conf" % remote_file)
        # Enter the sudo password
        stdin.write(password + '\n')
        stdin.flush()
        print('Mova %s to /etc/samba/smb.conf' % remote_file)

        stdin, stdout, stderr = ssh.exec_command(
            "sudo -S -p '' chown %s:%s /etc/samba/smb.conf" %
            (userid, usergroup))
        # Enter the sudo password
        stdin.write(password + '\n')
        stdin.flush()
        print('Change /etc/samba/smb.conf owner to %s:%s' %
              (userid, usergroup))

        stdin, stdout, stderr = ssh.exec_command(
            "sudo -S -p '' systemctl restart smbd")
        # Enter the sudo password
        stdin.write(password + '\n')
        stdin.flush()
        print('Restart samba service', end='')
        for i in range(5):
            sleep(1)
            sys.stdout.write('.')
            sys.stdout.flush()
        print()

    except Exception as e:
        print('\033[91m<<< CHMOD EXCEPTION!! >>>\033[0m', e)

    ssh.close()


def sftp_upload(*args):
    '''
    Upload local smb.conf file to remote host's home directory by sftp

    @ param host: <str> Remote host's IP.
    @ param port: <int> Remote host's port for sftp
    @ param username: <str> Remote host's login username for ssh.
    @ param password: <str> Remote host's login password for ssh.
    @ param local_file: <str> Local host upload file path.
    @ param remote_file: <str> Remote host upload file path.
    @ param filesmod: <int> The permission of upload files.
    '''
    paramiko.util.log_to_file('samba_sftp.log')
    host, port, username, password, local_file, remote_file, filesmod, userid, usergroup = args
    try:
        '''
        Create a new SSH session over an existing socket, or socket-like
        object. This only creates the Transport object; it doesn’t begin the
        SSH session yet.
        '''
        t = paramiko.Transport((host, port))
        '''
        Negotiate an SSH2 session, and optionally verify the server’s host
        key and authenticate using a password or private key
        '''
        t.connect(username=username, password=password)
        # Create an SFTP client channel from an open Transport.
        sftp = paramiko.SFTPClient.from_transport(t)
        print('\033[44m === UPDATE FILE TO %s START AT %s === \033[0m' %
              (host, datetime.datetime.now().strftime('%H:%M:%S')))

        sftp.put(local_file, remote_file)
        print("Upload %s to remote %s" % (local_file, remote_file))
        sftp.chmod(remote_file, filesmod)
        print("Change %s permission to %o" % (remote_file, filesmod))

        ssh_chmod(address, port, username, password,
                  remote_file, userid, usergroup)

        print('\033[44m === UPDATE FILE TO %s FINISH AT %s === \033[0m' %
              (host, datetime.datetime.now().strftime('%H:%M:%S')))
        print()
        t.close()

    except Exception as e:
        print()
        print('\033[91m<<< UPLOAD EXCEPTION!! >>>\033[0m', e)
        print()


def print_info(msg):
    print('\033[93m****************************************\033[0m')
    print('\033[93m*{:^38}*\033[0m'.format(msg))
    print('\033[93m****************************************\033[0m')


if __name__ == '__main__':
    # Read configuration from upload.ini
    try:
        config = configparser.ConfigParser()
        config.read('update.ini')
        address_list = config.get(
            'REMOTE', 'ipaddress').replace(' ', '').split(',')
        port = int(config.get('REMOTE', 'port'))
        username = config.get('REMOTE', 'username')
        password = config.get('REMOTE', 'password')
        local_file = config.get('LOCAL', 'filename')
        remote_file = config.get('REMOTE', 'filename')
        filesmod = int(config.get('REMOTE', 'filesmod'))
        userid = config.get('REMOTE', 'userid')
        usergroup = config.get('REMOTE', 'usergroup')
    except Exception as e:
        print('\033[91m<<< Read configuration FAIL! >>>\033[0m', e)
    print()
    print_info('IMPORT INI SUCCESS.')

    # Verify configuration information
    print('Read IP address list from INI file:', address_list)
    print('Read SSH port from INI file:', port)
    print('Read username from INI file:', username)
    print('Read password from INI file:', password)
    verify = input('Do you want to start update? (YES/no)')

    if verify == 'no':
        print_info('Byebye!')
    else:
        print()
        print_info('START UPDATE OPERATION.')
        for address in address_list:
            args = (address, port, username,
                    password, local_file,
                    remote_file, filesmod, userid, usergroup)
            sftp_upload(*args)
        print_info('ALL UPDATE SUCCESS.')
