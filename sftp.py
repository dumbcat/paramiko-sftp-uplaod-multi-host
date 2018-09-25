#!/usr/bin/python
# coding=utf-8

import paramiko
import os
import configparser
import datetime


def ssh_chmod(host, port, username, password, remote, dirpathmod):
    '''
    Change the permission of remote host's upload folder.

    @ param host: <str> Remote host's IP.
    @ param port: <int> Remote host's port for sftp
    @ param username: <str> Remote host's login username for ssh.
    @ param password: <str> Remote host's login password for ssh.
    @ param remote: <str> Remote host upload folder.
    @ param dirpathmod: <int> The permission of remote path.
    '''
    paramiko.util.log_to_file('ssh.log')

    ssh = paramiko.SSHClient()
    # Allow connections to hosts that are not in the know_hosts.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port=port, username=username, password=password)

    try:
        '''
        The -S flag tells sudu to expect the password to come from stdin
        The -p '' flag tells sudo to use '' or the empty string as the prompt
        for the password.
        The permission in Linux is a octal number, but in ini file is decimal.
        So use %o to transform decimal to octal.
        '''
        stdin, stdout, stderr = ssh.exec_command(
            "sudo -S -p '' chmod %o %s" % (dirpathmod, remote))
        # Enter the sudo password
        stdin.write(password + '\n')
        stdin.flush()
        print('\033[32m[ The %s permission of %s is changed to %o. ]\033[0m' %
              (host, remote, dirpathmod))
    except Exception as e:
        print('\033[91m<<< CHMOD EXCEPTION!! >>>\033[0m', e)

    ssh.close()


def sftp_upload(host, port, username, password, local, remote, filesmod):
    '''
    Upload local host's file and folder to remote host by sftp

    @ param host: <str> Remote host's IP.
    @ param port: <int> Remote host's port for sftp
    @ param username: <str> Remote host's login username for ssh.
    @ param password: <str> Remote host's login password for ssh.
    @ param local: <str> Local host upload folder.
    @ param remote: <str> Remote host upload folder.
    @ param filesmod: <int> The permission of upload files.
    '''
    paramiko.util.log_to_file('sftp.log')

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
        print('\033[44m === UPLOAD FILE TO %s START AT %s === \033[0m' %
              (host, datetime.datetime.now().strftime('%H:%M:%S')))

        for root, dirs, files in os.walk(local):
            '''
            os.walk will generate the file names in a directory tree by walking
            the tree. For each directory in the tree rooted at directory top
            (including top itself), it yields a 3-tuple (root, dirs, files).

            root: <str> The path to the directory.
            dirs: <list> The names of the subdirectories in dirpath (excluding
                  '.' and '..').
            file: <list> The names of the non-directory files in dirpath

            For example, if you want upload all files and floders in root to
            /html/ in remote host.
            root/(local)
             ├──home/
             │   └──note.txt
             ├──Pictures/
             ├──Music/
             │   └──hello.txt
             └──world.txt
            '''

            for filespath in files:
                '''
                Combine the path(root) with the file name(files) under the root
                become the file path.
                ex: /root/home/ + note.txt => /root/home/note.txt
                '''
                local_file_path = os.path.join(
                    root, filespath).replace("\\", "/")

                '''
                Delete the string of local(param) in the file path(local_file).
                ex: if local is /root/, /root/home/note.txt => home/note.txt
                '''
                local_file = local_file_path.replace(local, '')

                '''
                Combine the remote host path(remote) with local_file become
                remote file path.
                ex: /html/ + home/note.txt => /www/home/note.txt
                '''
                remote_file = os.path.join(remote, local_file)

                try:
                    sftp.put(local_file_path, remote_file)
                except Exception as e:
                    '''
                    An exception will be generated if the remote folder does
                    not exist. os.path.split will split the path(remote_file)
                    into (path, file). And use path to create the folder.
                    ex: /html/home/note.txt => ('/html/home/', 'note.txt')
                    '''
                    sftp.mkdir(os.path.split(remote_file)[0])
                    sftp.put(local_file_path, remote_file)
                # sftp.chmod's 2rd parma need provide decimal Linux permission.
                sftp.chmod(remote_file, filesmod)
                print("upload %s to remote %s" %
                      (local_file_path, remote_file))

            for name in dirs:
                '''
                If the local folder is empty, the above loop will not create an
                empty folder at the remote. This loop will do this.
                '''
                local_path = os.path.join(root, name)
                a = local_path.replace(local, '')
                remote_path = os.path.join(remote, a)
                try:
                    sftp.mkdir(remote_path)
                    print("mkdir path %s" % remote_path)
                except Exception as e:
                    # The exception will raise if the folder already exists.
                    pass

        print('\033[44m === UPLOAD FILE TO %s FINISH AT %s === \033[0m' %
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
        config.read('upload.ini')
        address_list = config.get(
            'REMOTE', 'ipaddress').replace(' ', '').split(',')
        port = int(config.get('REMOTE', 'port'))
        username = config.get('REMOTE', 'username')
        password = config.get('REMOTE', 'password')
        local = config.get('LOCAL', 'dirpath')
        remote = config.get('REMOTE', 'dirpath')
        dirpathmod = int(config.get('REMOTE', 'dirpathmod'))
        filesmod = int(config.get('REMOTE', 'filesmod'))
    except Exception as e:
        print('\033[91m<<< Read configuration FAIL! >>>\033[0m', e)
    print()
    print_info('IMPORT INI SUCCESS.')

    # Verify configuration information
    print('Read IP address list from INI file:', address_list)
    print('Read SSH port from INI file:', port)
    print('Read username from INI file:', username)
    print('Read password from INI file:', password)
    verify = input('Do you want to start uploading files? (YES/no)')
    if verify == 'no':
        print_info('Byebye!')
    else:
        print()
        print_info('START UPLOAD OPERATION.')
        for address in address_list:
            ssh_chmod(address, port, username, password, remote, dirpathmod)
            sftp_upload(address, port, username,
                        password, local, remote, filesmod)
        print_info('ALL UPLOAD SUCCESS.')
