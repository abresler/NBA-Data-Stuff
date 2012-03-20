#!/usr/bin/python
# connect.py - connect to the MySQL server

import sys
import MySQLdb as ms


# ver 1, import
def handcon(db='', h='', p='', u=''):
    db = db if db else "healthcaresas"
    h = h if h else 'localhost'
    u = u if u else 'sinn'
    try:
        conn = ms.connect(db        = db,
                          host      = h,
                          user      = u,
                          passwd    = p)
        print "Connected"
    except ms.Error, e:
        print 'Connection failed'
        print 'Error code: ', e.args[0]
        print 'Error message: ', e.args[1]
        sys.exit(1)

##    conn.close()
##    print "Disconnected"
    else:
        return conn

# ver 2, terminal
# use "python connect.py args" in txt file to fully automate...
'''
use option files, where option file in in MySQL format for vars:
import os
option_file = os.environ["HOME"] + '/' + file_name
conn = ms.connect(db = name, read_default_file = option_file)

'''
if __name__=='__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "d:h:p:u",
                                   ["db=", "host=", "password=", "user="])
    except getopt.error as e:
        # for errors, print out info
        print "%s: %s" % (sys.argv[0], e)
        sys.exit(1)
    # defualt conn parameter vals
    database    = 'cookbook'
    host_name   = 'localhost'
    password    = ''
    user_name   = 'sinn'
    # iterate over options
    for opt, arg in opts:
        if opt in ("-h", "--host"):
            host_name = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-u", "--user"):
            user_name = arg
        elif opt in ("-d", "--database"):
            database = arg
    # attempt to connect with handcon:
    conn = handcon(database, host_name, password, user_name)
