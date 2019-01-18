#!/usr/bin/python

import MySQLdb

db = MySQLdb.connect( host="onldb.starp.bnl.gov", user="sc", passwd="", db="Conditions_sc", port = 3502 )

cur = db.cursor()

cur.execute("SELECT * FROM tpcGridLeak") # this selects data from table tpcGridLeak in database Conditions_sc
#cur.execute("SELECT * FROM tpcPowerSupply")
#cur.execute("SHOW DATABASES") # this shows available databases

for row in cur.fetchall():
    print row


#cur.execute("SHOW TABLES") # this shows all tables that were created in Conditions_sc database
#for tb in cur:
#    print tb



db.close()
