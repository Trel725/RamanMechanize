from pywinauto.application import Application
from pywinauto.keyboard import SendKeys
import time
import datetime
import os
class RamanController(object):
	"""docstring for RamanController"""
	def __init__(self, path="C:\Program Files (x86)\EZRamanI 7B1\ProRaman L7B1 V829X3.exe"):
		super(RamanController, self).__init__()
		try:
			self.app=Application(backend="uia").connect(path=path)
			print("Found existing application, attaching...")
		except:
			print("Application not found, launching...")
			self.app=Application(backend="uia").start(path)
			time.sleep(5)
			self.app['EZRaman Reader  V8.2.0 MV'].wait("ready", timeout=100)
		
		self.w=self.app['EZRaman Reader  V8.2.0 MV']
		self.pb=self.w.ProgressBar
		self.path='C:\\AutoRaman\\Mapping\\'
		self.suffix=""

	def startScan(self):
		self.w.set_focus()
		SendKeys("{F1}")

	def waitForFinish(self):
		self.pb.wait("enabled")

	def makeScan(self):
		try:
			self.startScan()	
			self.waitForFinish()
		except Exception as e:
			print(str(e))
			pass

	def saveSpectrum(self, filename):
		timestamp=datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
		try:
			self.w.menu_select("File -> Save AS")
			SendKeys('{VK_DOWN}')
			SendKeys('{ENTER}')
			time.sleep(0.1) 
			SendKeys("C:{\}AutoRaman{\}"+filename+"_"+timestamp+".spc")
			SendKeys("{ENTER}")
		except Exception as e:
			print(str(e))
			pass

	def initializeFolder(self, dirname):
		timestamp=datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
		newpath=self.path+dirname+self.suffix
		if not os.path.exists(newpath):
			os.makedirs(newpath)
		else:
			self.suffix=timestamp
			newpath=self.path+dirname+self.suffix
			os.makedirs(newpath)


	def saveMapping(self, dirname, fname):
		timestamp=datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
		newpath=self.path+dirname+self.suffix
		try:
			self.w.menu_select("File -> Save AS")
			SendKeys('{VK_DOWN}')
			SendKeys('{ENTER}')
			time.sleep(0.1) 
			path=newpath+"\\"+fname
			SendKeys(path.replace("\\", "{\}"))
			SendKeys("{ENTER}")
		except Exception as e:
			print(str(e))
			pass

if __name__ == '__main__':  
	rc=RamanController()
	rc.startScan()
