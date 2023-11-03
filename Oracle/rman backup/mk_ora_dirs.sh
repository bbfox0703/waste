#!/bin/bash

## scripts directory
mkdir -p $HOME/scripts/rnam_log

## db backup directory @ CIFS or NFS
mkdir -p /db_backup/$HOSTNAME/rman_bck
mkdir -p /db_backup/$HOSTNAME/rman_zip
