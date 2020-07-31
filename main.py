import configparser

from ssh_functions import sftp_upload, ssh_chmod


def print_info(msg):
    print('\033[93m' + '*' * 40 + '\033[0m')
    print('\033[93m*{:^38}*\033[0m'.format(msg))
    print('\033[93m' + '*' * 40 + '\033[0m')


# Read configuration from upload.ini
config = configparser.ConfigParser()
if os.path.isfile('config/upload.ini'):
    config.read('config/upload.ini')
    try:
        address_list = config.get('REMOTE', 'ipaddress').split(',')
        port = int(config.get('REMOTE', 'port'))
        username = config.get('REMOTE', 'username')
        password = config.get('REMOTE', 'password')
        local_dir = config.get('LOCAL', 'dirpath')
        remote_dir = config.get('REMOTE', 'dirpath')
        dirpathmod = int(config.get('REMOTE', 'dirpathmod'))
        filesmod = int(config.get('REMOTE', 'filesmod'))
        sudo_password = config.get('REMOTE', 'sudo_password')

        print()
        print_info('IMPORT INI SUCCESS.')

        # Verify configuration information
        print('Read IP address list from INI file:', address_list)
        print('Read SSH port from INI file:', port)
        print('Read username from INI file:', username)
        print('Read password from INI file:', password)
        verify = input('Do you want to start uploading files? (y/n)')

        if verify != 'n':
            print()
            print_info('START UPLOAD PROCESS.')
            conn_err = []  # connect fail host list
            upload_err = []  # upload fail host list
            for address in address_list:
                conn_res = ssh_chmod(
                    address.strip(), port, username, password,
                    remote_dir, dirpathmod, sudo_password
                )
                if conn_res == 1:
                    upload_res = sftp_upload(
                        address, port, username, password,
                        local_dir, remote_dir, filesmod
                    )
                    if upload_res != 1:
                        upload_err.append(upload_res)
                else:
                    conn_err.append(conn_res)
            print_info('ALL PROCESSING FINISHED.')

            if len(conn_err) != 0:
                print('\033[91m<<< CONNECT FAIL HOST LIST >>>\033[0m')
                print(conn_err)
                print()
            if len(upload_err) != 0:
                print('\033[91m<<< UPLOAD FAIL HOST LIST >>>\033[0m')
                print(upload_err)
        else:
            print_info('Byebye!')

    except configparser.NoSectionError as e:
        print('\033[91m<<< Read configuration FAIL! >>>\033[0m', e)

    except configparser.NoOptionError as e:
        print('\033[91m<<< Read configuration FAIL! >>>\033[0m', e)
else:
    print('\033[91m<<< INI file not exist! >>>\033[0m')
