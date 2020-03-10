import numpy as np
from SerialCommunicator import SerialCommunicator
import time
import mss
from scipy.optimize import *


class AutoFocuser(object):
    """Performs focusing by finding maximal brightness"""

    def __init__(self, sc):
        # sc - an instance of SeriaCommunicator object
        super(AutoFocuser, self).__init__()
        self.sc = sc
        self.sct = mss.mss()
        self.monitor = {"top": 510, "left": 210, "width": 540, "height": 380}
        self.pos = 0
        self.bounds = [-5, 5]

    @staticmethod
    def rgb2gray(rgb):
        return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])

    def intensity(self, im):
        im = im[:, :, 2]  # red channel
        # im = self.rgb2gray(im)
        return im.max()  # np.percentile(im, 99)

    def get_frame(self):
        im = np.array(self.sct.grab(self.monitor))
        return im

    def move(self, step):
        self.sc.sendCommand("G91G0Z{0:4.3f}".format(step), read_resp=True)
        self.sc.sendCommand("G4P0.01", wait_for_ok=True, block=True)
        self.sc.sendCommand("G90")
        time.sleep(0.1)

    def loss(self, x):
        dx = x - self.pos
        self.move(dx)
        self.pos += dx
        i = self.intensity(self.get_frame())
        return -i

    def focus(self):
        res = minimize_scalar(self.loss, bounds=self.bounds,
                              method="bounded", tol=1e-2)
        return res.fun


if __name__ == '__main__':
    sc = SerialCommunicator("COM4")
    sc.initializeGrbl()
    time.sleep(2)
    print(sc.sendCommand("$X\n", read_resp=True))

    af = AutoFocuser(sc)
    res = af.focus()
    print(res.fun)
