from json import dump
import os
import time
import getpass

script_dir = os.path.dirname(os.path.realpath(__file__))  
origin_user = "root"
origin_password = "animesh987"
origin_host = ""
origin_database = "test1"
dest_user = "root"
dest_password = "animesh987"
dest_host = ""
dest_database ="test1"
include_routines = "y"

def db_backup():
    
    filestamp = time.strftime('%Y-%m-%d-%I:%M')
    dump_file = script_dir+"/"+origin_database+"_"+filestamp+".sql"
    if(include_routines.lower() == "y" or include_routines == ''):
        os.popen("mysqldump -u %s --password%s -h %s --default-character-set=utf8 --routines --ignore-table=%s.log %s --result-file %s" % (origin_user,origin_password,origin_host,origin_database,origin_database,dump_file))
    else:
        os.popen("mysqldump -u %s --password%s -h %s --default-character-set=utf8 --ignore-table=%s.log %s --result-file %s" % (origin_user,origin_password,origin_host,origin_database,origin_database,dump_file))

    print("Backup created at: ", dump_file)
    return dump_file

def db_recovery(path):

    #import mysql dump file
    os.popoen("mysql -u %s --password%s -h %s --default-character-set=utf8 %s < %s" % (dest_user,dest_password,dest_host,dest_database,path))
    print("Backup recovered at: ", path)