#!/usr/local/epics/modules/pythonIoc/pythonIoc


#import basic softioc framework
from softioc import softioc, builder

#import the the application
from TPC import TPC
tpc = TPC('130.199.60.15')

#run the ioc
builder.LoadDatabase()
softioc.iocInit()


# tpc.chlist[4].volt.set(78)
# print tpc.chlist[10].wboard, tpc.chlist[10].wch
# print tpc.dictpos[(1,2)]
# print tpc.chlist[10]

tpc.do_startthread()

#start the ioc shell
softioc.interactive_ioc(globals())
