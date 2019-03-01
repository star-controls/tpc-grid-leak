from softioc import builder, softioc
import subprocess
from epics import PV

class Channel():
    def __init__(self, sect_num, chann_num, wboard, wch, snmpset):
        self.sect_num = sect_num
        self.chann_num = chann_num
        self.wboard = wboard
        self.wch = wch
        self.cmdtemplate = snmpset
        base_PV = '{0:02d}:{1:d}:'.format(self.sect_num,self.chann_num)

        # Features of the channels
        self.volt = builder.aOut(base_PV+'setVoltage', on_update=self.setVoltage)
        self.curt = builder.aOut(base_PV+'setCurrent', on_update=self.setCurrent)
        self.wboardpv = builder.longIn(base_PV+'wboardpv', initial_value=self.wboard)
        self.wchpv = builder.longIn(base_PV+'wchpv', initial_value=self.wch)
        self.setOn = builder.boolOut(base_PV+'setOn', on_update=self.setOn, HIGH=0.1)
        self.setOff = builder.boolOut(base_PV+'setOff', on_update=self.setOff, HIGH=0.1)
        self.readVol = builder.aIn(base_PV+'readVol', PREC=1)
        if(self.chann_num==0):
            self.readVol.LOPR = 100
            self.readVol.HOPR = 130
            self.readVol.HIHI = 125
            self.readVol.HIGH = 120
            self.readVol.LOW  = 110
            self.readVol.LOLO = 105
            self.readVol.LSV = "MINOR"
            self.readVol.LLSV = "MAJOR"
            self.readVol.HSV = "MINOR"
            self.readVol.HHSV = "MAJOR"
        if(self.chann_num==1):
            self.readVol.LOPR = 400
            self.readVol.HOPR = 500
            self.readVol.HIHI = 470
            self.readVol.HIGH = 460
            self.readVol.LOW  = 440
            self.readVol.LOLO = 430
            self.readVol.LSV = "MINOR"
            self.readVol.LLSV = "MAJOR"
            self.readVol.HSV = "MINOR"
            self.readVol.HHSV = "MAJOR"
        self.readTem = builder.longIn(base_PV+'readTem')
        self.imon_read = 0. # measured current from ISEG
        self.imon_adj = 0. # adjustment to the measured current
        self.readCurr = builder.aIn(base_PV+'readCurr', PREC=2)
        self.status = builder.longIn(base_PV+'status')
        self.setReset = builder.boolOut(base_PV+'setReset', on_update=self.setReset, HIGH=0.1)

        if(self.wboard==0):
            self.a = str(self.wch)
        else:
            if(self.wboard !=0 and self.wch > 9):
                self.a = str(self.wboard)+str(self.wch)
            else:
                self.a = str(self.wboard)+'0'+str(self.wch)

    def adjust_measured_current(self):
        self.imon_adj = -1.*self.imon_read

    def put_measured_current(self):
        self.readCurr.set( self.imon_read + self.imon_adj )

    def setVoltage(self, val):
        print self.sect_num, self.chann_num, val
        cmd = '{0}outputVoltage.u{1} F {2:.1f}'.format(self.cmdtemplate, self.a, val)
        print cmd
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        out = p.communicate()

    def setCurrent(self, val):
        print self.sect_num, self.chann_num, val
        cmd = '{0}outputCurrent.u{1} F {2:.6f}'.format(self.cmdtemplate, self.a, val*1e-6)
        print cmd
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        out = p.communicate()

    def setOn(self, val):
        if(val==0):return
        print '{0}outputSwitch.u{1} i 1'.format(self.cmdtemplate, self.a)
        cmd = '{0}outputSwitch.u{1} i 1'.format(self.cmdtemplate, self.a)
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        out = p.communicate()

    def setOff(self, val):
        if(val==0):return
        print '{0}outputSwitch.u{1} i 0'.format(self.cmdtemplate, self.a)
        cmd = '{0}outputSwitch.u{1} i 0'.format(self.cmdtemplate, self.a)
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        out = p.communicate()

    def setReset(self, val):
        if(val==0):return
        cmd = '{0}outputSwitch.u{1} i 10'.format(self.cmdtemplate, self.a)
        print cmd
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        out = p.communicate()


