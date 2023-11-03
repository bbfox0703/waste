#!/bin/bash

## generate rman backup scriptlets

backup_root="/db_backup"

. $HOME/scripts/setEnv.sh

## Control file backup
echo "echo on;" >$HOME/scripts/backup_ctrl_f.sql
echo "set feedback ona;" >>$HOME/scripts/backup_ctrl_f.sql
echo "alter database backup controlfile to '$backup_root/$HOSTNAME/rman_bck/control01.bak' reuse;"  >>$HOME/scripts/backup_ctrl_f.sql
echo "exit" >>$HOME/scripts/backup_ctrl_f.sql

## spfile backup
echo "backup as copy spfile format '$backup_root/$HOSTNAME/rman_bck/spfile$ORACLE_SID.ora';" >$HOME/scripts/backup_spfile.txt


## full backup
echo "run" >$HOME/scripts/fullbackup.txt
echo "{" >>$HOME/scripts/fullbackup.txt
echo "sql 'alter database backup controlfile to trace';" >>$HOME/scripts/fullbackup.txt
echo "allocate channel ch1 type disk format '$backup_root/$HOSTNAME/rman_bck/"$ORACLE_SID"_full_%U';" >>$HOME/scripts/fullbackup.txt
echo "backup incremental level=0" >>$HOME/scripts/fullbackup.txt
echo "(database include current controlfile);" >>$HOME/scripts/fullbackup.txt
echo "sql 'alter system archive log current';" >>$HOME/scripts/fullbackup.txt
echo "sql 'alter system archive log current';" >>$HOME/scripts/fullbackup.txt
echo "sql 'alter system archive log current';" >>$HOME/scripts/fullbackup.txt
echo "backup format '$backup_root/$HOSTNAME/rman_bck/"$ORACLE_SID"_arch_%U'" >>$HOME/scripts/fullbackup.txt
echo "(archivelog all);" >>$HOME/scripts/fullbackup.txt
echo "release channel ch1;" >>$HOME/scripts/fullbackup.txt
echo "}" >>$HOME/scripts/fullbackup.txt
echo "exit;" >>$HOME/scripts/fullbackup.txt

