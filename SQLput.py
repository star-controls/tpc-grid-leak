import time
import threading
import MySQLdb

class SQLput():
    def __init__(self, channel):
        self.channel = channel
        r = threading.Thread(target=self.Write)
        r.daemon = True
        r.start()

    def Write(self):
        while True:
            time.sleep(30)
            unix_time = time.time()
            innerVolt, outerVolt = "", ""
            innerCurrent, outerCurrent = "", ""
            string_temp = "INSERT INTO tpcGridLeak (beginTime,VoltagesInner,VoltagesOuter,CurrentsInner,CurrentsOuter,Reason) VALUES (FROM_UNIXTIME({0:.0f}),\"".format(unix_time)
            reason = 0
            for i in range( len(self.channel) ):
                if( self.channel[i].status.get() == 4 ): reason = 6
                if( self.channel[i].chann_num == 0 ):
                    innerVolt = innerVolt + "{0:.2f}".format(self.channel[i].readVol.get())
                    innerCurrent = innerCurrent + "{0:.3f}".format(self.channel[i].readCurr.get())
                    if( i < len(self.channel)-2 ):
                        innerVolt = innerVolt + ";"
                        innerCurrent = innerCurrent + ";"
                if( self.channel[i].chann_num == 1 ):
                    outerVolt = outerVolt + "{0:.2f}".format(self.channel[i].readVol.get())
                    outerCurrent = outerCurrent + "{0:.3f}".format(self.channel[i].readCurr.get())
                    if( i < len(self.channel)-1 ):
                        outerVolt = outerVolt + ";"
                        outerCurrent = outerCurrent + ";"

            string_temp = string_temp + innerVolt + "\",\"" + outerVolt + "\",\"" + innerCurrent + "\",\"" + outerCurrent + "\"," + "{0}".format(reason) + ")"

            db = MySQLdb.connect( host="onldb.starp.bnl.gov", user="sc", passwd="", db="Conditions_sc", port = 3502 ) # open database
            cur = db.cursor()
            cur.execute(string_temp)
            db.commit()
            db.close()
            print "Insert done"
