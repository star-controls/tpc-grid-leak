import time
import pandas as pd
import threading
from Channel import Channel
from softioc import builder, softioc
builder.SetDeviceName('tpc_grid_leak')
import subprocess

class TPC():
    def __init__(self, ip):
        self.readData = builder.boolOut('readData', on_update=self.place_voltages, HIGH=0.1)
        self.on = builder.boolOut('on', on_update=self.turnOn, HIGH=0.1)
        self.off = builder.boolOut('off', on_update=self.turnOff, HIGH=0.1)
        self.avrgVolt = builder.aIn('avrgVolt')
        self.avrgTemp = builder.longIn('avrgTemp')
        self.marker = builder.longIn('marker')

        self.chlist = []
        self.wboard, self.wch = 0, 0
        self.ip = ip
        self.dictWiener, self.dictTPC = {}, {}
<<<<<<< HEAD
        file = open("file.txt","w")
        file.write("TPC sector \t TPC channel \t WIENER board \t WIENER channel \n")
        for self.i in xrange(1,25): # sector
            for self.j in xrange(2): # channel
=======
        file = open("file.txt","a")
        file.write("TPC sector \t TPC channel \t WIENER board \t WIENER channel \n")
        for self.i in xrange(1,25):
            for self.j in xrange(2):
>>>>>>> 368fa470ca14146e676e97b45922de2afefc75f5
                a = '{0} \t\t {1} \t\t {2} \t\t {3} \n'.format(self.i, self.j, self.wboard, self.wch)
                file.write(a)
                self.chlist.append(Channel(self.i, self.j, self.wboard, self.wch, self.ip))
                self.dictWiener[(self.wboard, self.wch)] = self.chlist[-1]
                self.dictTPC[(self.i, self.j)] = self.chlist[-1]
                self.wch+=1
                if(self.wch>15):
                    self.wboard+=1
                    self.wch=0
        file.close()
<<<<<<< HEAD
        print "Before start, you have to Load Voltage from file through Load Voltage button "
=======
>>>>>>> 368fa470ca14146e676e97b45922de2afefc75f5

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
            time.sleep(2)
            cmdV = "snmpwalk -v 2c -c starpublic 130.199.60.15 WIENER-CRATE-MIB::outputMeasurementSenseVoltage"
            cmdI = "snmpwalk -v 2c -c starpublic 130.199.60.15 WIENER-CRATE-MIB::outputMeasurementCurrent"
            cmdS = "snmpwalk -v 2c -c seCrET 130.199.60.15 WIENER-CRATE-MIB::outputStatus"
            cmdT = "snmpwalk -v 2c -c seCrET 130.199.60.15 WIENER-CRATE-MIB::outputMeasurementTemperature"
            eV, fV, gV = self.getValue(cmdV)
            eI, fI, gI = self.getValue(cmdI)

            p = subprocess.Popen(cmdS.split(), stdout=subprocess.PIPE)
            out = p.communicate()
            a = out[0].split('\n')

            pT = subprocess.Popen(cmdT.split(), stdout=subprocess.PIPE)
            outT = pT.communicate()
            aT = outT[0].split('\n') 

            sumV, sumT = 0, 0
            for j in range(len(eV)):
                ll = 99
                self.dictWiener[ (eV[j], fV[j]) ].readVol.set( gV[j]*(-1) )
                self.dictWiener[ (eI[j], fI[j]) ].readCurr.set( gI[j] )
                self.dictWiener[ (eI[j], fI[j]) ].readTem.set(int( aT[j].split()[-1] ))
                sumV = sumV + self.dictWiener[(eV[j], fV[j])].readVol.get()
                sumT = sumT + self.dictWiener[(eV[j], fV[j])].readTem.get()
                if('00 01' in a[j]):
                    ll=0 # OFF
                elif('80 11 80' in a[j]):
                    ll=2 # RAMP UP
                    if( self.dictWiener[ (eV[j], fV[j]) ].readVol.get() > self.dictWiener[ (eV[j], fV[j]) ].volt.get() ):
                        ll=3
                elif('80 09 80' in a[j]):
                    ll=3 # RAMP DOWN
                elif('80 01 80' in a[j]):
                    ll=1 # ON
                self.dictWiener[ (eI[j], fI[j]) ].status.set(ll)
            self.avrgVolt.set(sumV/len(eV))
            self.avrgTemp.set(sumT/len(eV))

    def do_startthread(self):
        t = threading.Thread(target=self.do_runreading)
        t.daemon = True
        t.start()

    def place_voltages(self, val):
        if val == 0: return
        f = pd.read_csv('data.csv')
        for line in range(len(f)):
            sektor = f['sektor'][line]
            tpcch = f['tpcch'][line]
            voltage = f['voltage'][line]
            self.dictTPC[(sektor, tpcch)].volt.set(voltage)

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
