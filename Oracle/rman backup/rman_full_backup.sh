#!/bin/bash

## RMAN backup main script

umask 022
. $HOME/scripts/setEnv.sh
# emails with space
DBALIST="my_email@my_domain.com";export DBALIST

NLS_LANG="AMERICAN_AMERICA.AL32UTF8";export NLS_LANG
NLS_DATE_FORMAT='YYYY-MM-DD HH24:MI:SS';export NLS_DATE_FORMAT
dt=$(date "+%Y%m%d_%H%M%S")
backup_root="/db_backup"
rman target / cmdfile=$HOME/scripts/del_backupset.txt log=$HOME/scripts/rman_log/$HOSTNAME_$dt.log
rm -rf $backup_root/$HOSTNAME/rman_bck/*
rman target / cmdfile=$HOME/scripts/backup_spfile.txt log=$HOME/scripts/rman_log/$HOSTNAME_$dt.log append
rman target / cmdfile=$HOME/scripts/fullbackup.txt log=$HOME/scripts/rman_log/$HOSTNAME_$dt.log append
rman target / cmdfile=$HOME/scripts/del_archive.txt log=$HOME/scripts/rman_log/$HOSTNAME_$dt.log append
sqlplus "/ as sysdba" @$HOME/scripts/backup_ctrl_f.sql >> $HOME/scripts/rman_log/$HOSTNAME_$dt.log append
sed '/Recovery Manager complete\|Starting backup at\|Finished backup at/!d' $HOME/scripts/rman_log/$HOSTNAME_$dt.log > $HOME/scripts/rman_log/temp.log
if [ `grep -o 'Recovery Manager complete' $HOME/scripts/rman_log/temp.log|wc -l` -ge 3 ] && [ `grep -o 'Finished backup at' $HOME/scripts/rman_log/temp.log|wc -l` -ge 3 ];then


iFile=$HOME/scripts/rman_log/$HOSTNAME_$dt.log
#if [ -s $iFile ] ; then
mailx -s "$ORACLE_SID on ${hostname}:DB RMAN Backup Successfully" $DBALIST < $HOME/scripts/rman_log/$HOSTNAME_$dt.log
else
mailx -s "$ORACLE_SID on ${hostname}:DB RMAN Backup Failure" $DBALIST < $HOME/scripts/rman_log/$HOSTNAME_$dt.log
fi ;

find $HOME/scripts/rman_log/*.log -mtime +14 -exec rm '{}' \;


####
SFILES=$backup_root/$HOSTNAME/rman_bck/*
DDIR=$backup_root/$HOSTNAME/rman_zip
for f in $SFILES
do
#  zip "$DDIR/$(basename $f).zip" $f
   zip "$DDIR/$dt.zip" $f
done
#####


find $backup_root/$HOSTNAME/rman_zip/*.zip -mtime +7 -exec rm '{}' \;

