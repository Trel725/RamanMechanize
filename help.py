from PyQt5 import QtCore, QtGui, QtWidgets
import sys



class HelpWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(HelpWindow, self).__init__(parent)
        self.setupUi(self)

    def setupUi(self, HelpWindow):
        HelpWindow.setObjectName("HelpWindow")
        #HelpWindow.resize(354, 287)
        self.centralwidget = QtWidgets.QWidget(HelpWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setReadOnly(True)
        self.horizontalLayout.addWidget(self.textEdit)
        HelpWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(HelpWindow)
        QtCore.QMetaObject.connectSlotsByName(HelpWindow)

    def showLincense(self):
        self.textEdit.setHtml(self.license)
        self.show()

    def showHelp(self):
        self.textEdit.setHtml(self.hlp)
        self.show()

    def retranslateUi(self, HelpWindow):
        _translate = QtCore.QCoreApplication.translate
        HelpWindow.setWindowTitle(_translate("HelpWindow", "HelpWindow"))

    hlp="""
 <h1 id="steppercontrol">Stepper Control</h1>

<p>This program is written to bring the capability of automated positioning and
program execution to microscope with stepper motors.</p>

<h2 id="usage">Usage</h2>

<ol>
<li><p>At first, the connection with stepper controller (running GRBL firmware) need to
be estblished. For this, select the serial port of controller in the 
drop-down menu and click connect. If you can't see the port of controller,
make sure it is connected and re-run the  program.</p></li>

<li><p>If connection is succeffully established, string "Initializing grbl"
should appear and current state of controller will be displayed on the 
top of window.</p></li>

<li><p>If absolute coordinate system is enabled, after initialization 
state will be changed to Alarm, showing that homing need to be performed.
This could be done by pressing "Start homing cycle" button.</p></li>

<li><p>After homing cycle, button "Go to central position" could be pressed
to perform centering.</p></li>

<li><p>Arrow keys may be used to navigate system to desired location. By pressing
"Add position to queue" current position will be saved to program.</p></li>

<li><p>By pressing "Add Raman to queue" the program will add the command of
spectrum gathering to the file, name of which could be specified in the
input field above the button.</p></li>

<li><p>Program could be made by subseqent adding of coordinates and raman
execution commands. Commands could be deleted or moved by mouse. 
Editing of command is possible by double clicking but is not recommended.</p></li>

<li><p>Program is activated by pressing "Start!" button. Execution details
are visible in the log window on the bottom. Program could be stopped
by pressing "Stop" or paused by pressing "Pause" button. Pausing will
take some time as current cycle need to be finished before pausing.</p></li>

<li><p>Programs could be saved and loaded by "Program" submenu in the top.</p></li>
</ol>

<h2 id="extrafeatures">Extra features</h2>

<h3 id="circle">Circle</h3>

<p>To automatically collect a few scans around one point, the circle mode could be used.
It is necessary to select number of point in the "points" window and corresponding 
radius in the nearby "rad" window. After this is done, by pressing "Circle" button
corresponding program will be added to the queue.</p>

<h3 id="mapping">Mapping</h3>

<p>Mapping is a method of obtaining information about chemical composition of the surface.
For that, two corners of the desired rectangular area need to be selected. For this</p>

<ol>
<li><p>Move to the first corner and press button "Corner 1"</p></li>

<li><p>Move to the second corner, press "Corner 2"</p></li>

<li><p>Modify, if necessary "dx" and "dy" values. which correspond to the step size
in X and Y direction respectivelly.</p></li>

<li><p>Press "Add Mapping" button and corresponding command will be generated and 
added to the queue.</p></li>
</ol>

<p>After generating any of the programs it need be started by pressing "Start" button</p>

<h2 id="trobleshooting">Trobleshooting</h2>

<p>Sometimes controller may be overloaded, which may occur in case of sudden
pressing of different arrow buttons in the same time. In that case reset
may be performed by pressing on the "STOP" button in the bottom. After that,
re-homing may be necessary.</p>
    """

    license="""<h1>GNU GPL v3.0</h1> <br/> 
    Source code is available at https://github.com/Trel725/RamanMechanize"""

def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = HelpWindow()  
    window.show()  
    app.exec_()  

if __name__ == '__main__':  
    main()  