# Enable fail2ban service for Debian OS / MariaDB & ssh connections

## Install necessary packages  
sudo apt install -y ufw rsyslog  
  
  
## Restart ssh service for enable login fail logging  
sudo systemctl restart sshd  
  
  
## Enable MariaDB error log to seperate file
  
### Edit MariaDB config  
sudo vi /etc/mysql/mariadb.conf.d/50-server.cnf  
>log_error = /var/log/mysql/error.log  

    
### Resatrt mariaDB service
sudo systemctl restart mariadb  

    
## Install fail2ban
sudo apt install -y fail2ban  

    
## Add filter
sudo vi /etc/fail2ban/filter.d/mariadb.conf  
  
>[INCLUDES]
>before = common.conf  
>  
>[Definition]  
>_daemon = mariadbd  
>failregex = ^%(__prefix_line)s(?:\d+ |\d{6} \s?\d{1,2}:\d{2}:\d{2} )?\[\w+\] Access denied for user '[^']+'@'<HOST>' (to database '[^']*'|\(using password: (YES|NO)\))*\s*$  
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
sudo ufw allow ssh  
sudo ufw allow mysql  
sudo ufw reload  
sudo ufw enable  

  
### i.e. other rules
sudo ufw allow from any to any port 10050 proto tcp  
sudo ufw allow from any to any port 161 proto udp  
sudo ufw allow 10050/tcp  

  
## check ufw status
sudo ufw status verbose  

    
## check fail2ban status
sudo systemctl restart fail2ban  
sudo systemctl status fail2ban  

    
## Try to  login fail for MariaDB several times  
  
## check fail2ban mariadb status
fail2ban-client status mariadb  

    
