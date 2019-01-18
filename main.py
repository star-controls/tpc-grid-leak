#!/usr/local/epics/modules/pythonIoc/pythonIoc


#import basic softioc framework
from softioc import softioc, builder

#import the the application
from TPC import TPC
from SQLput import SQLput
tpc = TPC('130.199.60.11')
sql = SQLput(tpc.chlist)

#run the ioc
builder.LoadDatabase()
softioc.iocInit()


# tpc.chlist[4].volt.set(78)
# print tpc.chlist[10].wboard, tpc.chlist[10].wch
# print tpc.dictpos[(1,2)]
# print tpc.chlist[10]

tpc.do_startthread()
tpc.readData.set(1)

#start the ioc shell
softioc.interactive_ioc(globals())
