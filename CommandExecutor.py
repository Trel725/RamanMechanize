import time
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from RamanController import RamanController
import numpy as np
class CommandExecutor(QThread):

    updateRow = pyqtSignal(int)
    def __init__(self):
        QThread.__init__(self)
        self.listWidget=None
        self.sc=None
    def __del__(self):
        self.wait()

    def decodeString(self, datastr):
        mydict={}
        datastr=datastr.replace(" ", "")
        for l in datastr.split(","): 
            (a,b)=l.split(":") 
            mydict[a]=b.strip()
        return mydict

    def Raman(self, filename):
        print("Starting signal collection to the file "+filename)
        self.ramanc.makeScan()
        self.ramanc.saveSpectrum(filename)
        time.sleep(1)
        print("Data is collected!")

    def scanCircle(self, x, y, radius, n, filename):
        steps=[]
        x=float(x)
        y=float(y)
        n=int(n)
        radius=float(radius)
        for theta in np.pi*np.linspace(0,2,n+1):
            steps.append([radius*np.cos(theta),radius*np.sin(theta)])
        i=1
        for (dx,dy) in steps[0:-1]:
            print("Scanning point {0} of circle".format(i))
            self.goToPos(x+dx, y+dy)
            self.Raman(filename+"_circle_"+str(i))
            self.goToPos(x,y)
            i=i+1

    def goToPos(self, x, y):
        resp=self.sc.sendCommand("G0X{0}Y{1}".format(x,y), read_resp=True)
        print("Going to coordinates X={0}, Y={1}".format(x, y))
        resp=self.sc.sendCommand("G4P0.01", wait_for_ok=True, block=True)
        print("Moving is finished")
        time.sleep(1)

    def run(self):
        for i in range(self.listWidget.count()):
            print("Row {0}: ".format(i), end="")

            self.updateRow.emit(i)
            item=self.listWidget.item(i)
            data=item.data(0)
            print(data)
            if data[0:5]=="Goto:":
                coords=data[5:].strip().split(";")
                (x,y)=(coords[0].strip(), coords[1].strip())
                self.goToPos(x, y)

            elif data[0:7] =="Circle:":
                param=self.decodeString(data[7:])
                print(param)
                try:
                    self.scanCircle(param['x'], param['y'],param['rad'], param['n'], param["fname"])
                except:
                    print("Can't parse the string, skipping...")

            elif data[0:5]=="Raman":
                filename=data.split(":")[1].strip()
                self.Raman(filename)
            else:
                print("Unknown command, skipping...")