# Check impedance connections of eeg electrodes (needs more development)

import sys
import time
import csv
import random

from PyQt5 import QtGui
from PyQt5.QtOpenGL import *
from PyQt5 import QtCore, Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygon

import numpy as np
import statistics as stats
from multiprocessing import Process, Queue

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes

SIMULATE = 0
FILE = 1
LIVESTREAM = 2

###########################################################

class impedance_win(QWidget):
    def __init__(self, hardware = None, model = None, sim_type = None, \
            data_type = None, serial_port = None, parent = None):
        super().__init__()

        self.parent = parent
        self.sim_type = sim_type
        self.hardware = hardware
        self.model = model
        self.serial_port = serial_port

        self.col_thresh = [65, 120, 200, 450, 800]
        self.col = [QtCore.Qt.green, QtCore.Qt.yellow, QtCore.Qt.darkYellow, QtCore.Qt.red, QtCore.Qt.black]

        self.electrodes = ["Fp1-Fp2","C3","P3","CZ","Cp1-Cp2","C4","P4","FZ"]
        self.chans_ind = "123456789"
        self.chan_num = 8

        self.coords = {
            "Fp1-Fp2"   :[0.00,  -0.08, 0.02], #Foward Frontal Lobe
            "C3"        :[-0.08,  0.00, 0.02], #Central Motor Cortex
            "P3"        :[-0.05,  0.10, 0.02], #Posterior Motor Cortex
            "CZ"        :[0.00,  0.00, 0.02], #Central Motor Cortex
            "Cp1-Cp2"   :[0.00,  0.05, 0.02], #Central-Posterior Motor Cortex
            "C4"        :[0.08,  0.00, 0.02], #Central Motor Cortex
            "P4"        :[0.05,  0.10, 0.02], #Posterior Motor Cortex
            "FZ"        :[0.00,  -0.04, 0.02], #Central Frontal Lobe
        }

        ### need a tertiary window to select which channels
            # a drop down for each channel - which deselects from a given if current selected
            # number of channel options is based on the model

        self.params = BrainFlowInputParams()

        if data_type == 'Task live':
            self.data_type = LIVESTREAM
        elif data_type == 'Task simulate':
            self.data_type = SIMULATE
        else:
            raise Exception('Unknown data type: {} Try "Task live" or "Task simulate"'.format(data_type))

        if self.data_type == LIVESTREAM:
            if self.hardware == 'openBCI':
                if self.model == 'Ganglion':
                    self.board_id = 1
                elif self.model == 'Cyton':
                    self.board_id = 0
                elif self.model == 'Cyton-Daisy':
                    self.board_id = 2
            self.params.serial_port = self.serial_port

        elif self.data_type == SIMULATE:
            self.board_id = -1

        # Brainflow Initialization

        # BoardShim.enable_dev_board_logger()

        self.setMinimumSize(800,800)
    
        # setting window title
        self.setWindowTitle('Impedance Window')
        
        # init layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        self.title_layout = QHBoxLayout()

        self.title = QLabel()
        self.title.setFont(QtGui.QFont('Arial',14))
        self.title.setText('Impedances')
        # self.title_layout.addWidget(self.title)

        self.layout.setContentsMargins(100,100,100,100)
        self.title_layout.setContentsMargins(50,50,50,50)

        self.layout.addLayout(self.title_layout,0,0,1,-1, QtCore.Qt.AlignHCenter)


        self.setLayout(self.layout)
        # self.layout.setContentsMargins(100,100,100,100)

        self.data = []
        self.running_test = False
        self.display_instructions()

        self.run = True

        self.color = QtCore.Qt.blue

        self.loop_timer = QTimer()
        # making it a precision timer
        self.loop_timer.setTimerType(0)
        self.loop_timer.setSingleShot(True)
        # setting the function to call when it times out
        # IMPORTANT: to change the function it calls, must first use timer.disconnect() to remove the previous one
        # otherwise will call both new and old fucntions
        self.loop_timer.timeout.connect(self.start_iteration)

        self.loop_running = False

        # To ensure we dont try to close the object a second time
        self.finished = False

        self.init_hardware()

    def init_hardware(self):

        # let's start eeg receiving!
        # self.start_data_stream()
        self.board = BoardShim(self.board_id, self.params)
        self.board.prepare_session()
        self.chan_ind = self.board.get_exg_channels(self.board_id)
        self.chan_num = len(self.chan_ind)
        print('init hardware is running with hardware',self.hardware,'model',self.model)

        self.hardware_connected = True

        # Think Pulse
        #self.board.config_board("x1040010Xx2040010Xx3040010Xx4040010Xx5040010Xx6040010Xx7040010Xx8040010XxQ040010XxW040010XxE040010XxR040010XxT040010XxY040010XxU040010XxI040010X")
        # Reinitialize the 15/16 channel for EOG
        # board.config_board("xU060100XxI060100X")

        #res = self.board.config_board("z110Zz210Zz310Zz410Zz510Zz610Zz710Zz810Zzq10Zzw10Zze10Zzr10Zzt10Zzy10Zzu10Zzi10Z")
        #print(res)

        self.board.start_stream(45000, None)
        self.impedances = [0] * self.chan_num

    def closeEvent(self, event):
        # this code will autorun just before the window closes
        # we will check whether streams are running, if they are we will close them
        print('close event works')
        self.on_end()

    def on_end(self):
        # called by end timer
        # self.stop_data_stream()
        # if self.is_end == False:

        self.board.stop_stream()
        self.board.release_session()


    def loop_start(self):
        print('starting loop')
        self.loop_running = True            
        self.loop_timer.timeout.disconnect()
        self.loop_timer.timeout.connect(self.start_iteration)
        self.loop_timer.start(1000)
        self.update()

    # def loop_end(self):
    #     print("ending loop")
    #     self.loop_running = False
    #     self.update()
    #     self.loop_timer.timeout.disconnect()
    #     self.loop_timer.timeout.connect(self.start_iteration)
    #     self.loop_timer.start(1000)

    def start_iteration(self):
        if not self.finished:
            time.sleep(1)
            self.data = self.board.get_board_data() # will need to be a consist number of samples
            for i in range(self.chan_num):
                # average with the prevous x number of fft data
                self.filter_custom(i)
                # print(len(self.data[i,:]))
                chan_std_uV = stats.stdev(self.data[i,:])
                self.impedances[i] = ((stats.sqrt( 2.0 ) * (chan_std_uV) * 1.0e-6) / 6.0e-9 - 2200)/100000
            print(self.impedances)
            '''
            HERE
            '''
            # need to do some smoothing from the past 6 seconds to take out instantaneous
            self.loop_start()
        else:
            print("exiting")
            time.sleep(2)
            self.on_end()

    def filter_custom(self, chan):
        DataFilter.perform_highpass(self.data[chan], BoardShim.get_sampling_rate(self.board_id), 1.0, 4,
                                        FilterTypes.BUTTERWORTH.value, 0)
        DataFilter.perform_bandstop(self.data[chan], BoardShim.get_sampling_rate(self.board_id), 60.0, 1.0, 3,
                                    FilterTypes.BUTTERWORTH.value, 0)

    def display_instructions(self):
        # this will run at the beginning and needs a button press before anything else will happen
        self.label = QLabel()
        self.label.setFont(QtGui.QFont('Arial',14))
        self.label.setText('Press enter once you have finished positioning the headset ')
        self.layout.addWidget(self.label)

    def keyPressEvent(self, event):
        if event.key() == Qt.Qt.Key_Space:
            print('received user input')
        elif event.key() == Qt.Qt.Key_Return or event.key == Qt.Qt.Key_Enter:
            if self.hardware_connected and not self.running_test:
                self.running_test = True
                self.label.setVisible(False)
                self.start_iteration()

    def paintEvent(self, event):
        # here is where we draw stuff on the screen
        # you give drawing instructions in pixels - here I'm getting pixel values based on window size
        print('paint event runs')
        painter = QPainter(self)
        if self.loop_running:
            radius = self.geometry().width()//18
            center = self.geometry().width()//2
            for i in range(self.chan_num):
                print(i)
                temp_coords = self.coords[self.electrodes[i]]
                x = temp_coords[0]*2500
                y = temp_coords[1]*2500
                temp_col = 0
                col_found = False
                for col in range(len(self.col_thresh)):
                    print(self.impedances[i])
                    # print(self.col_thresh[col])
                    print("Is impedance at electrode {} ({}) lower than threshhold ({}): {}".format(self.electrodes[i],self.impedances[i],self.col_thresh[col],self.impedances[i] < self.col_thresh[col]))
                    print("debug1: {}".format(col_found))
                    if col_found == False: 
                        print("debug2")
                        if self.impedances[i] < self.col_thresh[col]:
                            print("debug3")
                            temp_col = self.col[col]
                            print("therefor the colour of should be {}".format(self.col[col]))
                            col_found = True
                            # print("found colour")
                            # print(self.col_thresh[col])
                            # print(temp_col)
                if col_found == False:
                    temp_col = self.col[-1]
                painter.setBrush(QBrush(temp_col, QtCore.Qt.SolidPattern)) # QtCore.Qt.SolidPattern       
                painter.drawEllipse(center + x, center + y, radius, radius)
                painter.drawText(center + x - 30, center + y, self.electrodes[i] + ": " + str(self.impedances[i])) 
        elif self.finished:
            # no need to paint anything specifically
            pass

    def on_end(self):
        self.board.stop_stream()
        self.board.release_session()

if __name__ == '__main__':    
    app = QApplication(sys.argv)    
    win = impedance_win() 
    win.show() 
    sys.exit(app.exec())
