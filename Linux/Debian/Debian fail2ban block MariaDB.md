# Enable fail2ban service for Debian OS / MariaDB & ssh connections

## Install necessary packages  
sudo apt install -y ufw rsyslog  


## Restart ssh service
sudo systemctl restart sshd


## Enable MariaDB error log to seperate file

### Edit MariaDB config  
sudo vi /etc/mysql/mariadb.conf.d/50-server.cnf  
>log_error = /var/log/mysql/error.log  

### Resatrt service
sudo systemctl restart mariadb

## Install fail2ban
apt install -y fail2ban

## Add filter
vi /etc/fail2ban/filter.d/mariadb.conf

>[INCLUDES]
>before = common.conf
>
>[Definition]
>
>_daemon = mariadbd
>
>failregex = ^%(__prefix_line)s(?:\d+ |\d{6} \s?\d{1,2}:\d{2}:\d{2} )?\[\w+\] Access denied for user '[^']+'@'<HOST>' (to database '[^']*'|\(using password: (YES|NO)\))*\s*$
>
>ignoreregex =

## Add jail  
sudo vi /etc/fail2ban/jail.local  
>[mariadb]
>enabled   = true
>port      = 3306
>filter    = mariadb
>logpath   = /var/log/mysql/error.log
>findtime  = 300
>maxretry  = 4
>bantime   = 300

## generate login error (i.e. password incorrect) log for MariaDB

## test fail2ban RegEx
sudo fail2ban-regex /var/log/mysql/error.log /etc/fail2ban/filter.d/mariadb.conf

## add ufw rule
ufw allow ssh
ufw allow mysql
ufw reload
ufw enable

## check ufw status
ufw status verbose  

## check fail2ban status
systemctl restart fail2ban  
systemctl status fail2ban  

## check fail2ban mariadb status
fail2ban-client status mariadb
