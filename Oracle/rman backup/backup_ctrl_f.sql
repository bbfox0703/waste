set echo on
set feedback on
alter database backup controlfile to '/db_backup/<your_host_name>/rman_bck/control01.bak' reuse;
exit
