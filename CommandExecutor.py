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
        self.ramanc=RamanController()
        self.paused=False

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

    def Mapping(self, x0, y0, x1, y1, xres, yres, fname):
        self.ramanc.initializeFolder(fname)
        x0=float(x0)
        y0=float(y0)
        x1=float(x1)
        y1=float(y1)
        xs=np.array([x0,x1])
        ys=np.array([y0,y1])
        x0=xs.min()
        y0=ys.min()
        x1=xs.max()
        y1=ys.max()
        xres=float(xres)
        yres=float(yres)
        xgrid=np.arange(x0, x1+xres, xres)
        ygrid=np.arange(y0, y1+yres, yres)
        grid=np.meshgrid(xgrid, ygrid)
        coords=[]
        for i in zip(grid[0], grid[1]):
            for j in zip(i[0], i[1]):
                coords.append([j[0], j[1]])
        l=len(coords)
        for i, c in enumerate(coords):
            print("Scanning {0} point from {1}".format(i, l))
            if self.paused:
                print("Paused")
                while(self.paused):
                    time.sleep(0.1)
            self.goToPos(c[0], c[1])
            self.ramanc.makeScan()
            self.ramanc.saveMapping(fname, "x{0:4.3f}_y{1:4.3f}.spc".format(c[0], c[1]))
            time.sleep(0.1)

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
            if self.paused:
                print("Paused")
                while(self.paused):
                    time.sleep(0.1)
            print("Scanning point {0} of circle".format(i))
            self.goToPos(x+dx, y+dy)
            self.Raman(filename+"_circle_"+str(i))
            #self.goToPos(x,y)
            i=i+1

    def goToPos(self, x, y):
        x=float(x)
        y=float(y)
        resp=self.sc.sendCommand("G0X{0:4.3f}Y{1:4.3f}".format(x,y), read_resp=True)
        print("Going to coordinates X={0:4.3f}, Y={1:4.3f}".format(x, y))
        resp=self.sc.sendCommand("G4P0.01", wait_for_ok=True, block=True)
        print("Moving is finished")
        time.sleep(1)

    def run(self):
        for i in range(self.listWidget.count()):
            print("Row {0}: ".format(i), end="")
            if self.paused:
                print("Paused")
                while(self.paused):
                    time.sleep(0.1)
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
                #try:
                self.scanCircle(param['x'], param['y'],param['rad'], param['n'], param["fname"])
                #except:
                #    print("Can't parse the string, skipping...")

            elif data[0:5]=="Raman":
                filename=data.split(":")[1].strip()
                self.Raman(filename)

            elif data[0:4]=="Map:":
                param=self.decodeString(data[4:])
                self.Mapping(param['x1'], param['y1'], param['x2'], param['y2'], param['xres'], param['yres'], param['fname'])
            else:
                print("Unknown command, skipping...")