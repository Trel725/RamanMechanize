import sys
import design
import platform
import glob
import time
import serial
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QThread, QSettings, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from help import HelpWindow
from SerialCommunicator import SerialCommunicator
from CommandExecutor import CommandExecutor
from math import *


class JogSender(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.coord = [0, 0]
        self.sc = None
        self.DTime = 0.1
        self.feed = 10
        self.acc = 100
        self.single_step = False

    def __del__(self):
        self.wait()

    def resetFeed(self):
        self.feed = 10

    def generateJogCommand(self, coord, feed):
        multiplier = self.DTime * feed / 60
        x = coord[0] * multiplier
        y = coord[1] * multiplier
        cmd = "$J=G91X{:4.3f}Y{:4.3f}F{:4.3f}".format(x, y, feed)
        return cmd

    def run(self):
        while True:
            if self.single_step:
                cmd = self.generateJogCommand(self.coord, feed=1)
            else:
                cmd = self.generateJogCommand(self.coord, self.feed)

            resp = self.sc.sendCommand(cmd, wait_for_ok=False)

            self.feed += self.DTime * self.acc
            time.sleep(self.DTime * 0.95)


class Logger(QtCore.QObject):
    writeData = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.terminal = sys.stdout

    def write(self, message):
        self.writeData.emit(message)

    def flush(self):
        pass


class StepperControlGUI(QtWidgets.QMainWindow, design.Ui_MainWindow):

    def __init__(self):

        super().__init__()
        QtWidgets.QMainWindow.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        self.sc = None
        self.ce = CommandExecutor()
        self.ce.listWidget = self.listWidget
        self.ce.updateRow.connect(self.onrowChange)
        self.setzeroButton.clicked.connect(self.goZero)
        self.connectButton.clicked.connect(self.serial_connect)
        self.addposButton.clicked.connect(self.addCurrentPosition)
        self.StartExecutionButton.clicked.connect(self.startExecution)
        self.StopExecutionButton.clicked.connect(self.softReset)
        self.ramanButton.clicked.connect(self.addRamanCommand)
        self.homingButton.clicked.connect(self.startHoming)
        self.unlockButton.clicked.connect(self.unlock)
        self.addCircleButton.clicked.connect(self.addCircle)
        self.mapButton.clicked.connect(self.addMapping)
        self.topLeftButton.clicked.connect(self.topLeftCoord)
        self.botRightButton.clicked.connect(self.botRightCoord)
        self.actionLoad_program.triggered.connect(self.loadProgram)
        self.actionSave_program.triggered.connect(self.saveProgram)
        self.stopButton.clicked.connect(self.stopExecutor)
        self.pauseButton.clicked.connect(self.pauseExecutor)
        self.ce.finished.connect(self.execTerminated)
        self.settings = QSettings('VSCHT', 'StepperControl')
        self.selectSerialBox.addItems(self.list_serial_ports())
        if self.settings.contains("port"):
            saved_port = self.settings.value("port", type=str)
            try:
                idx = self.list_serial_ports().index(saved_port)
                self.selectSerialBox.setCurrentIndex(idx + 1)
            except Exception as e:
                pass

        self.DTime = 0.05
        self.startTimer(300)
        self.coordinates = [0, 0, 0]
        self.status = ""
        self.key_switcher = {
            Qt.Key_Right: [1.0, 0.0],
            Qt.Key_Left: [-1.0, 0.0],
            Qt.Key_Down: [0.0, -1.0],
            Qt.Key_Up: [0.0, 1.0],
        }
        self.key_pressed = {
            Qt.Key_Up: False,
            Qt.Key_Down: False,
            Qt.Key_Left: False,

            Qt.Key_Right: False,
        }

        self.js = JogSender()
        self.js.DTime = self.DTime
        # self.listWidget.installEventFilter(self)
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.openMenu)

        self.logger = Logger()
        self.logger.writeData.connect(self.writeDataToConsole)
        sys.stdout = self.logger

        self.mappoints = [[0, 0], [0, 0]]

        self.help = HelpWindow()
        self.actionUsage.triggered.connect(self.showHelp)
        self.actionLicense.triggered.connect(self.showLicense)

    def showHelp(self):
        self.help.showHelp()

    def showLicense(self):
        self.help.showLincense()

    def makeEnterFilename(self):
        txt = self.ramanFilename.text()
        while(len(txt) == 0 or txt == "raman_filename"):
            # QtWidgets.QMessageBox.warning(self, "Warning", "Please enter the file name")
            txt = QtWidgets.QInputDialog.getText(self, "Warning", "Please enter the file name")[0]
        self.ramanFilename.setText(txt)

    def execTerminated(self):
        self.StartExecutionButton.setEnabled(True)

    def pauseExecutor(self):
        if self.ce.isRunning():
            if self.pauseButton.text() == "Pause":
                self.ce.paused = True
                self.pauseButton.setText("Resume")
            else:
                self.ce.paused = False
                self.pauseButton.setText("Pause")

    def stopExecutor(self):
        if self.ce.isRunning():
            self.ce.terminate()
            print("Stopped!")

    def saveProgram(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Program', "c:/AutoRaman/Programs", filter="Text files (*.txt)", options=options)[0]
        txt = ""
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            txt += item.data(0) + "\r\n"
        if name[-4:] != ".txt":
            name += ".txt"
        file = open(name, 'w')
        file.write(txt)

    def loadProgram(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        name = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "c:/AutoRaman/Programs", "TXT(*.txt);;AllFiles(*.*)", options=options)[0]
        file = open(name, 'r')
        for line in file:
            line = line.replace('\n', "")
            line = line.replace('\r', "")
            if len(line) < 1:
                continue
            newitem = QtWidgets.QListWidgetItem(None)
            newitem.setData(0, line)
            newitem.setFlags(newitem.flags() | QtCore.Qt.ItemIsEditable)
            self.listWidget.addItem(newitem)

    @pyqtSlot(str)
    def writeDataToConsole(self, message):
        message = message.rstrip("\r")
        self.logger.terminal.write(message)
        self.logger.terminal.flush()
        self.consoleEdit.insertPlainText(message)
        self.consoleEdit.ensureCursorVisible()

    def openMenu(self, position):
        menu = QtWidgets.QMenu(self.listWidget)
        deleteAction = menu.addAction("Delete")
        editAction = menu.addAction("Edit")
        action = menu.exec_(self.listWidget.mapToGlobal(position))
        if action == deleteAction:
            self.listWidget.takeItem(self.listWidget.row(self.listWidget.currentItem()))
        elif action == editAction:
            self.listWidget.editItem(self.listWidget.currentItem())

    def list_serial_ports(self):
        system_name = platform.system()
        if system_name == "Windows":
            # Scan for available ports.
            available = []
            for i in range(256):
                port = "COM" + str(i)
                try:
                    s = serial.Serial(port)
                    available.append(port)
                    s.close()
                except serial.SerialException:
                    pass
            return available
        elif system_name == "Darwin":
            # Mac
            return glob.glob('/dev/tty*') + glob.glob('/dev/cu*') + glob.glob("/dev/ttyACM*")
        else:
            # Assume Linux or something else
            return glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob("/dev/ttyACM*")

    def serial_connect(self):
        selected = self.selectSerialBox.currentIndex()
        if selected in [0, -1]:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select serial port of the controller")
            return None
        port = self.selectSerialBox.itemText(selected)
        try:
            self.sc = SerialCommunicator(port)
            self.sc.initializeGrbl()
            self.js.sc = self.sc
            self.ce.sc = self.sc
            self.settings.setValue("port", port)
            self.settings.sync()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

    def softReset(self):
        if self.sc is not None:
            self.sc.soft_reset()

    def keyPressEvent(self, e):
        if not e.isAutoRepeat() and not self.js.isRunning():
            feed = 1000
            if e.key() in self.key_switcher.keys():
                self.key_pressed[e.key()] = True
                coord = self.key_switcher[e.key()]
                if self.sc is not None:
                    if self.SingleStepButton.isChecked():
                        self.js.single_step = True
                    else:
                        self.js.single_step = False
                    self.js.coord = coord
                    self.js.start()
                else:
                    QtWidgets.QMessageBox.warning(self, "Warning", "Please connect to the controller firstly")

    def updateCoordinates(self):
        if self.sc is not None:
            ret = self.sc.get_status()
            if ret is not None:
                try:
                    self.stateLabel.setText(ret['status'])
                    if ret['status'] == "Alarm":
                        self.stateLabel.setStyleSheet('color: red')
                    else:
                        self.stateLabel.setStyleSheet('color: black')
                    self.status = ret['status']
                    ret = ret["coordinates"]
                    self.coordinatesLCD.display("{0}:{1}:{2}".format(ret[0], ret[1], ret[2]))
                    self.coordinates = [ret[0], ret[1], ret[2]]
                except Exception as e:
                    print(e)
                    pass

    def timerEvent(self, e):
        self.updateCoordinates()
        self.checkAlarms()

    def keyReleaseEvent(self, e):
        if not e.isAutoRepeat():
            if e.key() in self.key_switcher.keys() and self.key_pressed[e.key()]:
                self.cancelJog()
                self.js.terminate()
                self.key_pressed[e.key()] = False
                self.js.resetFeed()
                self.cancelJog()
                if self.sc is not None:
                    self.sc.busy = False

    def cancelJog(self):
        if self.sc is not None:
            self.sc.ser.reset_output_buffer()
            self.sc.jog_cancel()

        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please connect to the controller firstly")

    def checkAlarms(self):
        if self.sc is not None:
            if self.sc.alarm is not None:
                txt = "ALARM"
                al = QtWidgets.QMessageBox()
                if self.sc.alarm == "3":
                    txt = "You need to start homing cycle!\n" + txt
                al.warning(self, "ALARM!", txt + self.sc.alarm)

                self.sc.alarm = None

    def goZero(self):
        if self.sc is not None:
            self.sc.sendCommand("G0X-28Y-38Z0", block=False)

    def addCurrentPosition(self):
        newitem = QtWidgets.QListWidgetItem(None)
        newitem.setData(0, "Goto: " + "; ".join(str(x) for x in self.coordinates))
        newitem.setFlags(newitem.flags() | QtCore.Qt.ItemIsEditable)
        self.listWidget.addItem(newitem)

    def addRamanCommand(self):
        self.makeEnterFilename()
        newitem = QtWidgets.QListWidgetItem(None)
        newitem.setData(0, "Raman: " + self.ramanFilename.text())
        newitem.setFlags(newitem.flags() | QtCore.Qt.ItemIsEditable)
        self.listWidget.addItem(newitem)

    def addCircle(self):
        newitem = QtWidgets.QListWidgetItem(None)
        self.makeEnterFilename()
        data = "Circle: x: {0}, y: {1}, rad: {2:4.3f}, n: {3}, fname: {4}".format(self.coordinates[0], self.coordinates[1],
                                                                                  self.radiusBox.value(), self.circlePointsBox.value(), self.ramanFilename.text())
        newitem.setData(0, data)
        newitem.setFlags(newitem.flags() | QtCore.Qt.ItemIsEditable)
        self.listWidget.addItem(newitem)

    def addMapping(self):
        newitem = QtWidgets.QListWidgetItem(None)
        self.makeEnterFilename()
        x1 = float(self.mappoints[0][0])
        y1 = float(self.mappoints[0][1])
        x2 = float(self.mappoints[1][0])
        y2 = float(self.mappoints[1][1])
        dx = float(self.xresBox.value())
        dy = float(self.yresBox.value())
        num = ceil(abs(x1 - x2) / dx + 1) * ceil(abs(y1 - y2) / dy + 1)
        reply = QMessageBox.question(self, 'Continue?',
                                     "Estimated number of points is {}\n Continue?".format(num),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        data = "Map: x1: {0}, y1: {1}, x2: {2}, y2: {3}, xres: {4:4.3f}, yres: {5:4.3f}, fname: {6}".format(x1, y1,
                                                                                                            x2, y2, dx, dy, self.ramanFilename.text())
        newitem.setData(0, data)
        newitem.setFlags(newitem.flags() | QtCore.Qt.ItemIsEditable)
        self.listWidget.addItem(newitem)

    def topLeftCoord(self):
        self.mappoints[0] = self.coordinates[0:2]

    def botRightCoord(self):
        self.mappoints[1] = self.coordinates[0:2]

    def startExecution(self):
        if self.sc is not None:
            self.ce.start()
            self.StartExecutionButton.setEnabled(False)
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please connect to the controller firstly")

    def startHoming(self):
        if self.sc is not None:
            ret = self.sc.sendCommand("$H", read_resp=True)
            if ret is not None:
                print("Error " + str(ret))
                return
            self.setzeroButton.setEnabled(True)
            self.sc.sendCommand("G55", read_resp=True)

    def unlock(self):
        if self.sc is not None:
            self.setzeroButton.setEnabled(False)
            self.sc.sendCommand("$X")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please connect to the controller firstly")

    @pyqtSlot(int)
    def onrowChange(self, value):
        item=self.listWidget.item(value)
        self.listWidget.setCurrentItem(item)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = StepperControlGUI()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
