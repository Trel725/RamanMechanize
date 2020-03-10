import serial
import time


class SerialCommunicator(object):
    """Class performing communatioin with GRBL software"""

    def __init__(self, port, baudrate=115200):
        super(SerialCommunicator, self).__init__()
        self.RX_BUFFER_SIZE = 127
        self.verbose = True
        self.alarm = None
        self.buf = None
        self.timeout = 50
        self.ser = serial.Serial(
            port, baudrate, timeout=self.timeout, write_timeout=self.timeout)
        self.busy = False

    def isOpen(self):
        return self.ser.is_open

    def sendCommand(self, command, read_resp=False, wait_for_ok=False, block=True):
        if block:
            self.busy = True
        command = command.strip().strip('\n')
        command += '\n'
        self.ser.reset_input_buffer()
        try:
            self.ser.write(command.encode())
        except Exception as e:
            print("Can't send the command to GRBL")
            print(str(e))
            pass

        if wait_for_ok:
            try:
                self.ser.reset_input_buffer()
                time.sleep(0.1)
                resp = self.ser.read_until("ok".encode())
                if resp.decode().find("ok") == -1:
                    time.sleep(10)
            except Exception as e:
                print("Can't get the \"OK\" responce, waiting...")
                print(str(e))
                time.sleep(10)
                pass
            self.busy = False
            return None
        if read_resp:
            try:
                resp = self.ser.readline().decode()
                # print(resp.encode())
            except Exception as e:
                print("Can't read response from after command was sent")
                print(str(e))
                time.sleep(0.1)
                self.busy = False
                return 255
            if resp.find('ok') > -1:
                self.busy = False
                return None
            elif resp.find('error') > -1:
                self.busy = False
                return resp.split(":")[1]
            else:
                self.busy = False
                return 255

    def initializeGrbl(self):
        print("Initializing grbl...")
        self.ser.write("\r\n\r\n".encode())
        time.sleep(0.5)
        resp = self.ser.read(size=self.ser.in_waiting)
        print("Got the response:", resp)
        self.ser.flush()

    def get_status(self):
        if not self.busy:
            # self.ser.reset_input_buffer()
            self.verifyBuffer()
            status, coord, fs = None, None, None
            keys = ['status', 'coordinates', 'fs']
            self.ser.write('?'.encode())
            time.sleep(0.1)
            try:
                resp = self.ser.read(size=self.ser.in_waiting).decode()
            except Exception as e:
                print("Can't read GRBL status response")
                print(str(e))
                return None
            # print(resp)

            resp = resp[resp.find("<") + 1:resp.find(">")]
            if len(resp) > 0:
                try:
                    resp = resp.split('|')
                    status = resp[0]
                    if resp[1][0:5] == "MPos:":
                        coord = resp[1][5:].split(',')
                    if resp[2][0:3] == "FS:":
                        fs = resp[2][3:].split(',')

                    ret = {}
                    for i, key in zip([status, coord, fs], keys):
                        if i is not None:
                            ret[key] = i
                    return ret
                except Exception as e:
                    print("Status responce is malformed")
                    print(str(e))
                    return None
                    pass
            else:
                return None

    def verifyBuffer(self):
        buf = self.ser.read(self.ser.in_waiting).decode()
        idx = buf.find("ALARM")
        if idx > -1:
            self.alarm = buf[idx + 6:idx + 7]
        self.ser.flushInput()

    def jog_cancel(self):
        try:
            self.ser.write(chr(0x85).encode())
        except Exception as e:
            print(str(e))
            pass

    def soft_reset(self):
        self.ser.write(chr(0x18).encode())
