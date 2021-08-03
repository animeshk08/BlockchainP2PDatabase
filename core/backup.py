import getpass
import os
import subprocess
import time
from json import dump

import environ

"""
Fetch environment variables from .env in parent directory
"""
env = environ.Env()
env.read_env('../.env')

script_dir = os.path.dirname(os.path.realpath(__file__))
origin_user = env("BACKUP_ORIGIN_DBUSER")
origin_password = env("BACKUP_ORIGIN_DBPASS")
origin_host = env("BACKUP_ORIGIN_DBHOST")
origin_database = env("BACKUP_ORIGIN_DBNAME")
dest_user = env("BACKUP_DESTINATION_DBUSER")
dest_password = env("BACKUP_DESTINATION_DBPASS")
dest_host = env("BACKUP_DESTINATION_DBHOST")
dest_database = env("BACKUP_DESTINATION_DBNAME")
include_routines = env("BACKUP_INCLUDE_ROUTINES")

"""
DB Backup utility function
"""
def db_backup():
    filestamp = time.strftime('%Y-%m-%d-%I:%M')
    dump_file = script_dir+"/"+origin_database+"_"+filestamp+".sql"
    if(include_routines.lower() == "y" or include_routines == ''):
        command = ("mysqldump -u %s --password=%s -h %s --default-character-set=utf8 --routines --ignore-table=%s.log %s --result-file %s --no-tablespaces" %
                   (origin_user, origin_password, origin_host, origin_database, origin_database, dump_file))
    else:
        command = ("mysqldump -u %s --password=%s -h %s --default-character-set=utf8 --ignore-table=%s.log %s --result-file %s --no-tablespaces" %
                   (origin_user, origin_password, origin_host, origin_database, origin_database, dump_file))

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return dump_file


"""
DB Recovery utility function
Dumps backup file in path passed to destination backup configs
"""
def db_recovery(path):
    # import mysql dump file
    command = ("mysql -u %s --password=%s -h %s --default-character-set=utf8 %s < %s" %
               (dest_user, dest_password, dest_host, dest_database, path))
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
