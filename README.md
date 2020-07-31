# Upload folder to multi remote host via SFTP

+ **Main Features**

  + Upload all files and folders in specify local directory to the specified directory of the multi remote host.

  + Modify the remote directory permissions to avoid upload failure due to insufficient user permissions.

  + Modify the permissions of the uploaded files and folders to avoid unable to execute the uploaded program due to insufficient permissions.


## Require Packages

+ configparser

+ paramiko

## Structure

+ **main&#46;py:** Read the ini file and execute the upload function, and finally display the upload result.

+ **ssh_functions&#46;py:** Execute chmod on the remote host via ssh, and upload local directory to remote host via SFTP.

+ **config/upload.ini:** Parameters needed to run the program.
# INI file

+ **Remote host:**

<pre><code>[REMOTE]
ipaddress = <i>&lt;remote host 1 IP>, &lt;remote host 2 IP>, &lt;remote host 3 IP></i>
port = <i>&lt;remote host ssh port></i>
username = <i>&lt;remote host ssh login username></i>
password = <i>&lt;remote host ssh login password></i>
sudo_password = <i>&lt;password required to execute sudo></i>
dirpath = <i>&lt;remote host upload destination folder></i>
dirpathmod = <i>&lt;the remote host directory permissions before upload></i>
filesmod = <i>&lt;the remote host directory permissions after upload></i></code></pre>

+ **Local host:**

<pre><code>[LOCAL]
dirpath = <i>&lt;the directory to upload from the local host></i></code></pre>

## Attention
In the Linux system, the permissions are **three octet numbers**, such as 777 and 755. But octet numbers cannot be use in ini file.

So dirpathmod and filesmod in the ini file must be set to decimal numbers. For example, **the decimal of 755 is 493, and the decimal of 777 is 511.**


# Reference

&#91;1] http://blog.51cto.com/wangwei007/1285412

&#91;2] http://docs.paramiko.org/en/stable/