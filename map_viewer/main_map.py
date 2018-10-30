import sys  
import os  
import spc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QSizePolicy
from PyQt5.QtGui import QIntValidator
from mapdesign import Ui_MainWindow
import glob
from map import MapEntry
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib import cm

from scipy.interpolate import griddata, bisplrep, bisplev

class PlotCanvas(FigureCanvas):
 
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #self.ax = fig.gca(projection='3d')
        self.ax = self.fig.gca()
        self.ax1=self.fig.add_axes()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
 
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
      
        super().__init__()
        self.setupUi(self) 
        self.directory=None 
        self.actionOpen_Folder.triggered.connect(self.get_directory)
        self.spectra=[]
        self.dxSpinBox.setValue(0.1)
        self.pltWidget = PlotCanvas(self, width=5, height=5)
        self.pltWidget.move(0,0)
        self.verticalLayout.addWidget(self.pltWidget)
        self.addToolBar(NavigationToolbar(self.pltWidget, self))
        self.interpcheckBox.stateChanged.connect(self.checkbox_handler)
        self.freqEdit.returnPressed.connect(self.freq_box_handler)
        self.slider.valueChanged.connect(self.update_handler)
        self.dxSpinBox.valueChanged.connect(self.update_handler)
        self.orderBox.valueChanged.connect(self.update_handler)
        self.methodBox.currentIndexChanged.connect(self.method_box_handler)
        self.smoothSpinBox.valueChanged.connect(self.update_handler)
        self.cb=None
        self.interp=None
        val=QIntValidator()
        self.freqEdit.setValidator(val)
        self.method="CT"

    def method_box_handler(self):
        if self.methodBox.currentText()=="Spline":
            self.method="spline"
        else:
            self.method="CT"
        self.update_handler()


    def freq_box_handler(self):
        self.slider.setValue(int(self.freqEdit.text()))

    def checkbox_handler(self):
        if self.interpcheckBox.isChecked():
            self.interp=self.dxSpinBox.value()
        else:
            self.interp=None
        self.plot(self.slider.value())

    def update_handler(self):
        self.plot(self.slider.value())

    def plot(self, value):
        if len(self.spectra)==0:
            return 0
        xs,ys,zs=[],[],[]
        for i in self.spectra:
            xs.append(i.x)
            ys.append(i.y)
            zs.append(i.find_nearest_y(value))
        self.pltWidget.ax.clear()
        
        if self.cb is not None:
            self.cb.remove()

        if self.interp:
            xnew, ynew, znew = self.interpolate(xs, ys, zs, self.interp, method=self.method)
            if len(znew.shape)<2:
                znew=znew.reshape(ynew.shape[0], xnew.shape[0]).T
            im=self.pltWidget.ax.pcolormesh(ynew, xnew, znew)
            self.cb=self.pltWidget.fig.colorbar(im)
            self.pltWidget.draw()
            self.freqEdit.setText(str(value))
            return


        im=self.pltWidget.ax.hexbin(xs, ys, C=zs, cmap=cm.jet, bins=None)
        self.cb=self.pltWidget.fig.colorbar(im)
        self.pltWidget.draw()
        self.freqEdit.setText(str(value))

    def interpolate(self,x,y,z,dx, method="CT"):
        x=np.array(x)
        y=np.array(y)
        z=np.array(z)
        order=self.orderBox.value()
        points=np.stack([x,y]).T
        xnew = np.arange(min(x), max(x)+dx, dx)
        ynew = np.arange(min(y), max(y)+dx, dx)
        if method=="spline":
            tck = bisplrep(x, y, z, s=self.smoothSpinBox.value(), kx=order, ky=order)
            znew = bisplev(xnew[:-1], ynew[:-1], tck)
            return xnew, ynew, znew
        g = np.meshgrid(xnew, ynew)
        positions = np.vstack(map(np.ravel, g))
        return xnew, ynew, griddata(points, z, positions.T, fill_value=0.0, method="cubic", rescale=True)

    def get_directory(self):
        pth = str(QFileDialog.getExistingDirectory(self, "Select Directory", "c:/AutoRaman/Mapping"))
        if len(pth)<2:
            return 
        self.scan_for_spc(pth)
        if len(self.spectra) < 1:
            return
        datax=self.spectra[0].datax
        self.slider.setMinimum(datax.min())
        self.slider.setMaximum(datax.max())
        self.plot(1000)

    def scan_for_spc(self, pth):
        counter=0
        for file in glob.iglob(pth+'/**/'+"*.spc", recursive=True):
            print("Working with", file)
            s=spc.File(file)
            fname=os.path.basename(file)
            fname=os.path.splitext(fname)[0]
            coords=fname.split("_")
            for i in coords:
                if i[0]=='x':
                    x=float(i[1:])
                if i[0]=='y':
                    y=float(i[1:])
            try:
                entry=MapEntry(s.x, s.sub[0].y)
                entry.x, entry.y = x, y
                self.spectra.append(entry)
                counter+=1
            except Exception as e:
                print("Can't proceed file ", file)
                print(str(e))
                raise(e)
                pass
        print("{0} files successfully added".format(counter))




def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = ExampleApp()  
    window.show()  
    app.exec_() 

if __name__ == '__main__': 
    main()  