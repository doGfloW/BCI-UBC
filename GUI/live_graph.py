import sys

#from IPython.display import clear_output


# from pyqtgraph.Qt import QtGui, QtCore
# import pyqtgraph as pg
# import random
from pyOpenBCI import OpenBCICyton
import threading
import time
# import numpy as np
# from scipy import signal
from serial import Serial

def print_raw(sample):
    print(sample.channels_data)

board = OpenBCICyton(port='COM5', daisy=False)

def start_cyton():
    try:
        board.start_stream(print_raw)
    except:
        pass

y = threading.Thread(target=start_cyton)
y.daemon=True
y.start()

time.sleep(.02)
board.disconnect()