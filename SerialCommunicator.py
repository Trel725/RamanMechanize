import serial
import time

class SerialCommunicator(object):
	"""docstring for SerialCommunicator"""
	def __init__(self, port, baudrate=115200):
		super(SerialCommunicator, self).__init__()
		self.RX_BUFFER_SIZE=127
		self.verbose=True
		self.alarm=None
		self.buf=None
		self.timeout=50
		self.ser=serial.Serial(port, baudrate, timeout=self.timeout, write_timeout=self.timeout)
		self.busy=False


	def isOpen(self):
		return self.ser.is_open

	def sendCommand(self, command, read_resp=False, wait_for_ok=False, block=True):
		if block:
			self.busy=True
		command=command.strip().strip('\n')
		command+='\n'
		self.ser.reset_input_buffer()
		try:
			self.ser.write(command.encode())
		except:
			pass
		if wait_for_ok:
			try:
				self.ser.reset_input_buffer()
				time.sleep(0.1)
				resp=self.ser.read_until("ok".encode())
				if resp.decode().find("ok")==-1:
					time.sleep(10)
			except:
				time.sleep(10)
				pass
			self.busy=False
			return None
		if read_resp:
			try:
				resp=self.ser.readline().decode()
				#print(resp.encode())
			except:
				time.sleep(0.1)
				self.busy=False
				return 255
			if resp.find('ok') >-1:
				self.busy=False
				return None
			elif resp.find('error') >-1:
				self.busy=False
				return resp.split(":")[1]
			else:
				self.busy=False
				return 255


	def initializeGrbl(self):
		print("Initializing grbl...")
		self.ser.write("\r\n\r\n".encode())
		time.sleep(0.5)
		resp=self.ser.read(size=self.ser.in_waiting)
		print("Got the response:", resp)
		self.ser.flush()
		

	def get_status(self):
		if not self.busy:
			status, coord, fs=None, None, None
			keys=['status', 'coordinates', 'fs']
			self.ser.write('?'.encode())
			try:
				resp=self.ser.read(size=self.ser.in_waiting).decode()
			except:
				return None
			#print(resp)
			self.verifyBuffer(resp)		
			resp=resp[resp.find("<")+1:resp.find(">")]
			if len(resp)>0:
				try:
					resp=resp.split('|')
					status=resp[0]
					if resp[1][0:5]=="MPos:":
						coord=resp[1][5:].split(',')
					if resp[2][0:3]=="FS:":
						fs=resp[2][3:].split(',')

					ret={}
					for i, key in zip([status, coord, fs], keys):
						if i is not None:
							ret[key]=i
					return ret
				except:
					return None
					pass
			else:
				return None

	def verifyBuffer(self, buf):
		idx=buf.find("ALARM")
		if idx > -1:
			self.alarm=buf[idx+6:idx+7]
		self.ser.flushInput()

	def jog_cancel(self):
		try:
			self.ser.write(chr(0x85).encode())
		except:
			pass

	def soft_reset(self):
		self.ser.write(chr(0x18).encode())

	def SerialStream(self, f):
		'''communicates with grbl by sending commands line-by-line from f'''

		l_count=0
		g_count = 0
		c_line = []
		f=f.split('\n')
		for line in f:
			l_count += 1 # Iterate line counter
			l_block = line.strip().strip('\n')
			c_line.append(len(l_block)+1) # Track number of characters in grbl serial read buffer
			grbl_out = ''
			print(sum(c_line), self.ser.inWaiting()) 
			while sum(c_line) >= self.RX_BUFFER_SIZE-1 or self.ser.inWaiting() :
				out_temp = self.ser.readline().strip().decode() # Wait for grbl resp
				print("otemp", out_temp)
				if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
					print("Debug: ", out_temp) # Debug resp
				else :
					grbl_out += out_temp;
					g_count += 1 # Iterate g-code counter
					grbl_out += str(g_count); # Add line finished indicator
					del c_line[0] # Delete the block character count corresponding to the last 'ok'
			if self.verbose: print("SND: " + str(l_count) + " : " + l_block,)
			self.ser.write(l_block.encode() + '\n'.encode()) # Send g-code block to grbl
			if self.verbose : print("BUF:",str(sum(c_line)),"REC:",grbl_out)






