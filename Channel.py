from softioc import builder, softioc
import subprocess
from epics import PV

class Channel():
    def __init__(self, sect_num, chann_num, wboard, wch, ip):
        self.sect_num = sect_num
        self.chann_num = chann_num
        self.wboard = wboard
        self.wch = wch
        self.ip = ip
        base_PV = '{0:02d}:{1:d}:'.format(self.sect_num,self.chann_num)

# Features of the channels
        self.volt = builder.aOut(base_PV+'setVoltage', on_update=self.setVoltage)
        self.wboardpv = builder.longIn(base_PV+'wboardpv', initial_value=self.wboard)
        self.wchpv = builder.longIn(base_PV+'wchpv', initial_value=self.wch)
        self.setOn = builder.boolOut(base_PV+'setOn', on_update=self.setOn, HIGH=0.1)
        self.setOff = builder.boolOut(base_PV+'setOff', on_update=self.setOff, HIGH=0.1)
        self.readVol = builder.aIn(base_PV+'readVol')
        self.readTem = builder.longIn(base_PV+'readTem')
        self.readCurr = builder.aIn(base_PV+'readCurr')
        self.status = builder.longIn(base_PV+'status')

        self.cmdtemplate = "snmpset -v 2c -c seCrET "+str(self.ip)+" WIENER-CRATE-MIB::"
        if(self.wboard==0):
            self.a = str(self.wch)
        else:
            if(self.wboard !=0 and self.wch > 9):
                self.a = str(self.wboard)+str(self.wch)
            else:
                self.a = str(self.wboard)+'0'+str(self.wch)

    def setVoltage(self, val):
        print self.sect_num, self.chann_num, val
        print '{0}outputVoltage.u{1} F {2:.1f}'.format(self.cmdtemplate, self.a, val)
        cmd = '{0}outputVoltage.u{1} F {2:.1f}'.format(self.cmdtemplate, self.a, val)
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


# snmpset -v 2c -c seCrET 130.199.60.15 WIENER-CRATE-MIB::outputSwitch.u0 i 1
# snmpset -v 2c -c seCrET 130.199.60.15 WIENER-CRATE-MIB::outputVoltage.u0 F 5.0
