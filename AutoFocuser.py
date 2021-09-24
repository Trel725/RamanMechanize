import numpy as np
from SerialCommunicator import SerialCommunicator
import time
import mss
from scipy.optimize import *
from scipy.ndimage.filters import *


class AutoFocuser(object):
    """Performs focusing by finding maximal brightness"""

    def __init__(self, sc):
        # sc - an instance of SeriaCommunicator object
        super(AutoFocuser, self).__init__()
        self.sc = sc
        self.sct = mss.mss()
        self.monitor = {"top": 510, "left": 210, "width": 540, "height": 380}
        self.pos = 0
        self.bounds = [-2, 2]
        self.modes = {'intensity': self.measure_intensity,
                      'edges': self.measure_int_edges}
        self.mode = 'intensity'

    @staticmethod
    def rgb2gray(rgb):
        return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])

    def measure_edges(self, im):
        return -1 * np.abs(gaussian_gradient_magnitude(im, sigma=3)).sum() / im.size

    def measure_intensity(self, im):
        red = im[:, :, 2]  # red channel
        # im = self.rgb2gray(im)
        return -1 * red.max() / 255.0

    def select_mode(self, mode):
        assert mode in self.modes, "Unsupported mode"
        self.mode = mode

    def measure_int_edges(self, im):
        return self.measure_intensity(im), 1 * self.measure_edges(im)

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
        i = self.modes[self.mode](self.get_frame())
        # print(i)
        try:
            return sum(i)
        except:
            return i

    def focus(self):
        res = minimize_scalar(self.loss, bounds=self.bounds,
                              method="bounded", tol=1e-2)
        return res.fun


if __name__ == '__main__':
    sc = SerialCommunicator("COM5")
    sc.initializeGrbl()
    time.sleep(2)
    print(sc.sendCommand("$X\n", read_resp=True))

    af = AutoFocuser(sc)
    res = af.focus()
    print(res)
