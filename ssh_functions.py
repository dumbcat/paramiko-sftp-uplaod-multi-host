import datetime
import os

import paramiko


def ssh_chmod(host, port, username, password, remote_dir, dirpathmod, sudo_password):
    """Change the permission of the remote host folder.

    Args:
        host (string): Remote host IP address.
        port (integer): Remote host SSH port.
        username (string): SSH login username for the remote host.
        password (string): SSH login password for the remote host.
        remote_dir (string): The destination folder in the remote host.
        dirpathmod (integer): The decimal permission of the destination
            folder which wants to change.
        sudo_password (string): The root password in the remote host.

    Returns:
        integer: Return 1 if chmod executes success.

    Raises:
        Exception: If SSH connects or chmod executes fail. In the meantime
            return remote host IP address.
    """
    paramiko.util.log_to_file(f'logs/ssh-{datetime.date.today()}.log')
    ssh = paramiko.SSHClient()
    # Allow connections to hosts that are not in the know_hosts.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname=host, port=port,
                    username=username, password=password)
        print('\033[32m<<< Connected to %s >>>\033[0m' % host)
        # -S: Receive the password from the stdin instead of the terminal.
        # -p '': Change the prompt symbol for requset password.
        # %o: Transform the permission from decimal to octal.
        # The permission in Linux is a octal number, but in ini file is decimal.
        stdin, stdout, stderr = ssh.exec_command(
            "sudo -S -p '' chmod %o %s" % (dirpathmod, remote_dir))
        # Input the sudo password
        stdin.write(sudo_password + '\n')
        stdin.flush()
        return 1
    except Exception as e:
        print('\033[91m<<< CONNECT %s EXCEPTION!! >>>\033[0m %s ' % (host, e))
        print()
        return host
    ssh.close()


def sftp_upload(host, port, username, password, local_dir, remote_dir, filesmod):
    """Upload the directory in the local host to the remote host by sftp.   

    Args:
        host (string): Remote host IP address.
        port (integer): Remote host SSH port.
        username (string): SSH login username for the remote host.
        password (string): SSH login password for the remote host.
        local_dir (string): The directory in the local host.
        remote_dir (string): Upload destination folder in the remote host.
        filesmod (integer): The decimal permission of the destination
            file which wants to change.

    Returns:
        integer: Return 1 if sftp upload success.

    Raises:
        Exception: [description]
    """
    paramiko.util.log_to_file(f'logs/sftp-{datetime.date.today()}.log')

    try:
        t = paramiko.Transport((host, port))
        t.connect(username=username, password=password)
        # Create an SFTP client channel from an open Transport object.
        sftp = paramiko.SFTPClient.from_transport(t)
        print('\033[44m === UPLOAD FILE TO %s START AT %s === \033[0m' %
              (host, datetime.datetime.now().strftime('%H:%M:%S')))

        for root, folders, files in os.walk(local_dir):
            '''
            root: <str> The path to each directory in the local_dir.
            dirs: <list> The folders in the root (excluding '.' and '..').
            file: <list> The files in the root, not include in the dirs.
            '''
            # Upload all files in local_dir.
            for f in files:
                # Generate file path by combine root with the file name in it.
                local_file_path = os.path.join(
                    root, f).replace("\\", "/")

                # Generate the file path under the local_dir.
                local_file = local_file_path.replace(local_dir, '')

                # Generate file path in remote host
                remote_file = os.path.join(remote_dir, local_file)

                try:
                    sftp.put(local_file_path, remote_file)
                except:
                    sftp.mkdir(os.path.split(remote_file)[0])
                    sftp.put(local_file_path, remote_file)
                sftp.chmod(remote_file, filesmod)
                print("upload %s to remote %s" %
                      (local_file_path, remote_file))

            # Upload all folders in local_dir.
            # Avoid empty folders will not be created in the previous loop.
            for folder in folders:
                local_path = os.path.join(root, folder)
                relative_path = local_path.replace(local_dir, '')
                remote_path = os.path.join(remote_dir, relative_path)
                try:
                    sftp.mkdir(remote_path)
                    print("mkdir path %s" % remote_path)
                except:
                    # The exception will raise if the folder already exists.
                    pass

        print('\033[44m === UPLOAD FILE TO %s FINISH AT %s === \033[0m' %
              (host, datetime.datetime.now().strftime('%H:%M:%S')))
        print()
        t.close()
        return 1

    except Exception as e:
        print()
        print('\033[91m<<< UPLOAD %s EXCEPTION!! >>>\033[0m %s' % (host, e))
        print()
        return host
