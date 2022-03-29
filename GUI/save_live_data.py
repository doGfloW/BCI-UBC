import argparse
import time
import numpy as np
import pandas as pd
import sys
import csv 

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes

#PyQT5 GUI Imports
from PyQt5 import QtCore, Qt
from PyQt5.QtCore import QTimer, QTime, Qt, QEventLoop
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel,QWidget, QHBoxLayout
from PyQt5.QtGui import QFont, QPainter, QBrush

#matlab import
import matlab.engine
from short_movement import kanova

#Program Constants
SIMULATE = 0
FILE = 1
LIVESTREAM = 2

#Class: live control Window
class live(QWidget):
    def __init__(self, hardware=None, model=None, sim_type=None, \
                 data_type=None, csv_name=None, parent=None,
                 arduino_port=None, serial_port=None):
        super().__init__()
        BoardShim.enable_dev_board_logger()
        self.parent = parent
        self.sim_type = sim_type
        self.hardware = hardware
        self.model = model

        self.params = BrainFlowInputParams()
        self.params.serial_port = serial_port

        # BoardShim.enable_dev_board_logger()
        # MANUALLY SPECIFY COM PORT IF USING CYTON OR CYTON DAISY
        # if not specified, will use first available port
        # should be a string representing the COM port that the Cyton Dongle is connected to.
        # e.g for Windows users 'COM3', for MacOS or Linux users '/dev/ttyUSB1
        self.com_port = None

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
        elif self.data_type == SIMULATE:
            self.board_id = -1


        
        # iniszzilse matlab
        self.m = matlab.engine.start_matlab()
        # Pyqt setup
        self.setMinimumSize(900, 900)
        self.mainlayout=QVBoxLayout()
        self.layout1 = QVBoxLayout()
        fnt = QFont('Open Sans', 40, QFont.Bold)
        
        self.setWindowTitle('Live Control')
        self.lbl = QLabel()
        self.lbltext=QLabel()
        self.lbl.setAlignment(Qt.AlignHCenter)
        self.lbltext.setAlignment(Qt.AlignHCenter)
        self.lbl.setFont(fnt)
        self.lbltext.setFont(fnt)
        self.layout1.addWidget(self.lbl)
        self.layout1.addWidget(self.lbltext)
        self.layout1.addStretch(1)
        self.mainlayout.addLayout(self.layout1)
        self.setLayout(self.mainlayout)

        self.rawdata="live_raw_data.txt"
        self.run=True
        self.data=[]
        self.temp_result=0
        self.instructions()
        #self.savedata()

    def instructions(self):
        self.lbltext.setText("Instructions:\n Think about moving your right arm to move the robot\nPress Enter to start")
        self.start=True
        self.arm_run=False
        #self.lbltext.setVisible(True)
        
    # method for Key event
    def keyPressEvent(self, event):
            if self.start == True and self.arm_run==False and event.key() == Qt.Key_Return:
                #self.lbltext.clear(
                self.timer = QTimer()
                self.timer.timeout.connect(self.savedata)  # execute `display_time`
                self.timer.setInterval(5000)  # 1000ms = 1s
                self.timer.start()
                

    # def movement(self):
    #     self.lbltext.setText('move your right hand\nuntill timer stops')

    def savedata (self):

            self.data=[]
            # Setting up the board
            self.board = BoardShim(self.board_id, self.params)
            self.board.prepare_session()
            self.hardware_connected = True
            self.board.start_stream()
            time.sleep(1)
            self.data = self.board.get_board_data() # gets data from borad
            DataFilter.write_file(self.data, self.rawdata, 'w')
            self.board.stop_stream()
            self.board.release_session()
            # feature extration
            data_txtfile = r"live_raw_data.txt"
            rms_result, bp_vals, rms_vals = self.m.bp_rms_extraction(data_txtfile, nargout=3)
            bp_vals = list(bp_vals[0])
            rms_vals = list(rms_vals[0])
            rms_result=int(rms_result)
            rms_result=str(rms_result)
            # a=[]
            # a.append(rms_result)
            # rms_result=a
            # print(a)
            #rms_vals= np.array(rms_vals) 
            print("rms vlaes")
            print(rms_vals)
            # RMS classification
            #rms_result =self.m.RMS_classification(rms_vals)
            #rms_result = list(rms_result[0])
            print("rms classification")
            print(rms_result)
            # Bandpower classification
            # bp_result =self.m.RMS_classification(bp_vals)
            # bp_result = list(bp_result[0])


            # compere classification results
            # if bp_result==rms_result:
            #     self.arm_out= rms_result
            #     self.temp_result=self.arm_out


            # else :
            #     self.arm_out=self.temp_result 

            self.arm_out= rms_result
            self.write_classification()
            self.arm_run=True

            self.arm_control() # call arm control
            self.run=False
            self.start = True

        
            
    def arm_control (self):
        # function for controling robotic arm
        kanova()
        self.arm_run=False
        print(self.start,self.arm_run)
    def write_classification(self):
        # open the file in the write mode
        with open('Live_data/classifaction.txt', 'w') as f:

            f.write(self.arm_out)

    def closeEvent(self, event):
            # called by end timer
            self.run=False
            self.board.stop_stream()
            self.board.release_session()
            print('stop eeg stream ran')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mibaseline_win()
    main.show()
    sys.exit(app.exec())
