import time
import pandas as pd
import threading
from Channel import Channel
from softioc import builder, softioc, alarm
builder.SetDeviceName('tpc_grid_leak')
import subprocess

class TPC():
    def __init__(self, ip):
        self.readData = builder.boolOut('readData', on_update=self.place_voltages, HIGH=0.1)
        self.on = builder.boolOut('on', on_update=self.turnOn, HIGH=0.1)
        self.off = builder.boolOut('off', on_update=self.turnOff, HIGH=0.1)
        self.avrgVolt = builder.aIn('avrgVolt')
        self.avrgTemp = builder.longIn('avrgTemp')
        self.avrgVoltInner = builder.aIn('avrgVoltInner')
        self.avrgVoltOuter = builder.aIn('avrgVoltOuter')
        self.marker = builder.longIn('marker')
        self.setVoltInner_pv = builder.aOut("setVoltInner", on_update=self.setVoltInner)
        self.setVoltOuter_pv = builder.aOut("setVoltOuter", on_update=self.setVoltOuter)
        self.write_voltages_pv = builder.boolOut("write_voltages", on_update=self.write_voltages, HIGH=0.1)
        self.datacsv = "data.csv"
        self.reset = builder.boolOut("reset", on_update=self.Reset, HIGH=0.1)
        self.adj_current_pv = builder.boolOut("adj_current", on_update=self.adj_current, HIGH=0.1)
        self.adj_current_csv = "adj_current.csv"

        self.chlist = []
        self.wboard, self.wch = 0, 0
        self.ip = ip
        self.dictWiener, self.dictTPC = {}, {}

        #snmp 5.8 for user defined precision in current readings, compiled according to
        # http://file.wiener-d.com/software/net-snmp/net-snmp-CompileForExtendedPrecision-2015-03-06.txt
        self.snmpwalk = "/usr/local/Net-SNMP_5-8/code/apps/snmpwalk"
        self.snmpset = "/usr/local/Net-SNMP_5-8/code/apps/snmpset -v 2c -c seCrET "+self.ip+" WIENER-CRATE-MIB::"

        file = open("file.txt","w")
        file.write("TPC sector \t TPC channel \t WIENER board \t WIENER channel \n")
        for self.i in xrange(1,25): # sector
            for self.j in xrange(2): # channel
                a = '{0} \t\t {1} \t\t {2} \t\t {3} \n'.format(self.i, self.j, self.wboard, self.wch)
                file.write(a)
                self.chlist.append(Channel(self.i, self.j, self.wboard, self.wch, self.snmpset))
                self.dictWiener[(self.wboard, self.wch)] = self.chlist[-1]
                self.dictTPC[(self.i, self.j)] = self.chlist[-1]
                self.wch+=1
                if(self.wch>15):
                    self.wboard+=1
                    self.wch=0
        file.close()
        print "Before start, you have to Load Voltage from file through Load Voltage button "

    def getValue(self, cm):
            p = subprocess.Popen(cm.split(), stdout=subprocess.PIPE)
            out = p.communicate()
            a = out[0].split("\n")
            l1, l2, l3 = [], [], []
            for i in range(0,len(a)-1):
                b = a[i].split('.u')
                c = b[1].split()
                if( len( c[0] ) == 1):
                    iboard=0
                    ich = int(c[0])
                elif( len( c[0] ) == 2):
                    iboard=0
                    ich=int(c[0])
                else:
                    iboard = int(c[0][0])
                    ich = int(c[0][1:])
                if iboard >2: continue # we use only boards 0, 1, 2
                l1.append(iboard)
                l2.append(ich)
                l3.append(float(c[4]))
            return l1,l2,l3

    def do_runreading(self):
        while True:
            time.sleep(1) # default was 2 sec
            cmd_base = self.snmpwalk + " -v 2c -c starpublic " + self.ip + " WIENER-CRATE-MIB::"
            cmdV = cmd_base + "outputMeasurementSenseVoltage"
            cmdI = cmd_base + "outputMeasurementCurrent -Op .8"
            cmdS = cmd_base + "outputStatus"
            cmdT = cmd_base + "outputMeasurementTemperature"
            try: 
                eV, fV, gV = self.getValue(cmdV)
                eI, fI, gI = self.getValue(cmdI)
            except IndexError:
                print "Wiener crate not responding"
                self.set_invalid()
                continue

            if len(eV) == 0:
                print "Empty response from Wiener crate"
                self.set_invalid()
                continue

            p = subprocess.Popen(cmdS.split(), stdout=subprocess.PIPE)
            out = p.communicate()
            a = out[0].split('\n')

            pT = subprocess.Popen(cmdT.split(), stdout=subprocess.PIPE)
            outT = pT.communicate()
            aT = outT[0].split('\n') 

            sumV, sumT = 0, 0
            sumVi, sumVo = 0, 0
            Ni, No = 0, 0
            for j in range(len(eV)):
                ll = 99
                try:
                    self.dictWiener[ (eV[j], fV[j]) ].readVol.set( gV[j]*(-1) )
                    wch = self.dictWiener[ (eI[j], fI[j]) ]
                    wch.imon_read = gI[j]*1e6
                    wch.put_measured_current()
                    self.dictWiener[ (eI[j], fI[j]) ].readTem.set(int( aT[j].split()[-1] ))
                except:
                    print "Invalid value from Wiener response"
                    self.set_invalid()
                    continue

                sumV = sumV + self.dictWiener[(eV[j], fV[j])].readVol.get()
                sumT = sumT + self.dictWiener[(eV[j], fV[j])].readTem.get()
                if('00 01' in a[j]):
                    ll=0 # OFF
                #if('80 11 80' in a[j] or '80 01' in a[j] or '80 11' in a[j] or '80 21' in a[j]):
                if('80 11 80' in a[j] or '80 21' in a[j] or '80 01 outputOn(0)' in a[j]):
                #if('80 11 80' in a[j]):
                    ll=2 # RAMP UP
                    if( self.dictWiener[ (eV[j], fV[j]) ].readVol.get() > self.dictWiener[ (eV[j], fV[j]) ].volt.get() ):
                        ll=3
                if('80 09 80' in a[j]):
                    ll=3 # RAMP DOWN
                if('80 01 80' in a[j]):
                    ll=1 # ON
                if('04 01' in a[j]):
                    ll=4 # TRIP
                self.dictWiener[ (eI[j], fI[j]) ].status.set(ll)
                #report unrecognized status to ioc shell
                if ll > 10:
                    print "Unrecognized channel status:", ll, j, a[j]

            for ch in self.chlist:
                if(ch.chann_num==0): 
                    Ni+=1
                    sumVi = sumVi + ch.readVol.get()
                if(ch.chann_num==1):
                    No+=1
                    sumVo = sumVo + ch.readVol.get()

            self.avrgVoltInner.set(sumVi/Ni)
            self.avrgVoltOuter.set(sumVo/No)
            self.avrgVolt.set(sumV/len(eV)) # total average volt = inner + outer
            self.avrgTemp.set(sumT/len(eV))

    def do_startthread(self):
        t = threading.Thread(target=self.do_runreading)
        t.daemon = True
        t.start()

    def set_invalid(self):
        for ch in self.chlist:
            ch.readVol.set_alarm(alarm.INVALID_ALARM, alarm=alarm.UDF_ALARM)
            ch.readTem.set_alarm(alarm.INVALID_ALARM, alarm=alarm.UDF_ALARM)
            ch.readCurr.set_alarm(alarm.INVALID_ALARM, alarm=alarm.UDF_ALARM)
            ch.status.set_alarm(alarm.INVALID_ALARM, alarm=alarm.UDF_ALARM)

        self.avrgVolt.set_alarm(alarm.INVALID_ALARM, alarm=alarm.UDF_ALARM)
        self.avrgTemp.set_alarm(alarm.INVALID_ALARM, alarm=alarm.UDF_ALARM)
        self.marker.set_alarm(alarm.INVALID_ALARM, alarm=alarm.UDF_ALARM)

    def place_voltages(self, val):
        if val == 0: return
        f = pd.read_csv(self.datacsv)
        for line in range(len(f)):
            sektor = f['sektor'][line]
            tpcch = f['tpcch'][line]
            voltage = f['voltage'][line]
            current = f['current'][line]
            self.dictTPC[(sektor, tpcch)].volt.set(voltage)
            self.dictTPC[(sektor, tpcch)].curt.set(current)

    def write_voltages(self, val):
        if val == 0: return
        f = pd.read_csv(self.datacsv)
        for i in xrange(len(f)):
            sec = f['sektor'][i]
            ch = f['tpcch'][i]
            volt = self.dictTPC[(sec, ch)].volt.get()
            curr = self.dictTPC[(sec, ch)].curr.get()
            f['voltage'][i] = volt
            f['current'][i] = curr
        f.to_csv(self.datacsv, index=False)

    def turnOn(self, val):
        self.marker.set(1)
        if val == 0: return
        for obj in self.chlist:
            obj.setOn.set(1)

    def turnOff(self, val):
        self.marker.set(2)
        if val == 0: return
        for obj in self.chlist:
            obj.setOff.set(1)

    def setVoltInner(self, val):
        for ch in self.chlist:
            if ch.chann_num != 0: continue
            ch.volt.set(val)

    def setVoltOuter(self, val):
        for ch in self.chlist:
            if ch.chann_num != 1: continue
            ch.volt.set(val)

    def Reset(self, val):
        if(val==0):return
        for obj in self.chlist:
            if(obj.status.get()==4):
                print "RESET: sector {0}, channel{1}".format(obj.sect_num, obj.chann_num)
                obj.setReset.set(1)

    def adj_current(self, val):
        if val == 0: return
        for ch in self.chlist:
            ch.adjust_measured_current()


