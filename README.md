# 程式說明
+ sftp.py
    + 本程式開發於Python 3.7
    + 上傳指定本機目錄下的所有檔案與資料夾(包括空資料夾)到多個遠端目錄下。
    + 修改遠端目錄權限，避免因登入權限不足而無法上傳。
    + 修改被上傳的檔案與資料夾的權限，避免因權限不足而無法執行上傳後的程式。

+ updatesamba.py
    + 本程式開發於Python 3.7
    + 專為上傳smb.conf使用，上傳smb.conf到指定至多個遠端主機
    + 上傳後會執行chmod修改指定權限、mv移動到/etc/samba/smb.conf、chown修改到指定使用者與群組、重新啟動samba服務

# 環境
+  pip -r requirements.txt 安裝所需套件

# INI檔說明

## upload.ini for sftp.py

### 遠端主機設定部分:

    [REMOTE]
    ipaddress = 192.168.1.187, 192.168.1.188, 192.168.1.189
    port = 22
    username = moxa
    password = moxa
    dirpath = /var/www/html/
    dirpathmod = 511
    filesmod = 493 

**ipaddress**
遠端主機IP位址，如有多台主機可用「,」分隔
**port**
遠端主機SSH埠口
**username**
遠端主機登入使用者名稱
**password**
遠端主機登入使用者密碼
**dirpath**
遠端主機上傳目錄
**dirpathmod**
遠端主機上傳目錄(dirpath)欲修改的權限
**filesmod**
被上傳的檔案與目錄欲修改的權限

***注意: Linux系統中權限為三位八進位數字，如777、755，但ini讀入時無法讀入八進位數字，所以ini檔中 dirpathmod 與 filesmod 必須設定為十進位數字。如755的十進位為493，777的十進位為511。***

### 本地主機設定部分:

    [LOCAL]
    dirpath = ./test/

**dirpath**
本地主機欲上傳的檔案與目錄所存放的位置，可用絕對路徑或相對路徑，程式會上傳設定資料夾以下(不包含設定資料夾)的所有檔案與目錄。

## update.ini for updatesamba.py

### 遠端主機設定部分:
    [REMOTE]
    ipaddress = 192.168.1.100, 192.168.1.187
    port = 22
    username = moxa
    password = moxa
    filename = /home/moxa/smb.conf
    ; The permission dirpath.
    ; chmod need enter a decimal
    ; 755(octal) -> 493(decimal)
    ; 777(octal) -> 511(decimal)
    filesmod = 420
    userid=root
    usergroup=root

**ipaddress**
遠端主機IP位址，如有多台主機可用「,」分隔
**port**
遠端主機SSH埠口
**username**
遠端主機登入使用者名稱
**password**
遠端主機登入使用者密碼
**filename**
smb.conf上傳至遠端主機路徑
**filesmod**
smb.conf上傳至遠端主機後要變更的權限
**userid**
smb.conf上傳至遠端主機後要變更的使用者
**usergroup**
smb.conf上傳至遠端主機後要變更的群組

***注意: Linux系統中權限為三位八進位數字，如777、755，但ini讀入時無法讀入八進位數字，所以ini檔中filesmod 必須設定為十進位數字。如755的十進位為493，777的十進位為511。***

### 本地主機設定部分:

    [LOCAL]
    filename = ./smb.conf

**filename**
本地主機欲上傳的smb.conf的位置，可用絕對路徑或相對路徑。

# 參考文件
+ [程式碼實現](http://blog.51cto.com/wangwei007/1285412)
+ [Paramiko文件](http://docs.paramiko.org/en/2.4/index.html)