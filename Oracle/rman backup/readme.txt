rman backup script example
Enviornment: Oracle Linux 8 / Oracle 12c R2 / bash shell

use at your own risk!!
Edit these scripts before running it!!

Pre-requirements:
Install and setup mailx
basic bash knowledge
basic Oracle knowledge

Steps:
1. run mk_ora_dirs.sh to build directory
2. copy all files to $HOME/scripts
3. edit & run setEnv.sh for Oracle env. variables
4. run gen_scriptlet.sh to generate rman scriptlets
5. run rman_full_backup.sh to perform a full backup
6. put rman_full_backup.sh in crontab for regular full backup

rman_full_backup.sh:
perform a full rman backup
keep backup for 7 days
compress old backup with zip
email result with mailx