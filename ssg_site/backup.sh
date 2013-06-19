#!/bin/bash
_now=$(date +"%F_%T")
_file="/srv/i5058/backups/$_now.sql"
echo "starting ..."
/usr/pgsql-9.2/bin/pg_dump feedstrap > "$_file" -U postgres
echo "Done!"
