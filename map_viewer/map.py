import numpy as np

class MapEntry(object):
	def __init__(self, datax, datay, fname=None):
		super(MapEntry, self).__init__()
		self.datax=datax
		self.datay=datay
		self.x=0
		self.y=0
		self.fname = fname


	def find_nearest_y(self, value):
	    array = np.asarray(self.datax)
	    idx = (np.abs(self.datax - value)).argmin()
	    return self.datay[idx]
