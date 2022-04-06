import argparse
import time
from turtle import Turtle, update
import numpy as np
import pandas as pd
import sys
import csv 
import random
import winsound

# board imports
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes

# PyQt5 GUI imports
from PyQt5 import QtCore, Qt
from PyQt5.QtCore import QTimer, QTime, Qt, QEventLoop
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPainter, QBrush

# Matlab import
import matlab.engine
from short_movement import kanova

# program constants
SIMULATE = 0
FILE = 1
LIVESTREAM = 2


# class: Live Control Window
class live(QWidget):
    def __init__(self, hardware=None, model=None, sim_type=None,
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

        # check if the task is live or simulated
        if data_type == 'Task live':
            self.data_type = LIVESTREAM
        elif data_type == 'Task simulate':
            self.data_type = SIMULATE
        else:
            raise Exception('Unknown data type: {} Try "Task live" or "Task simulate"'.format(data_type))

        # if the task is live and OpenBCI hardware, get the board type
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

        # initialize Matlab connection
        self.m = matlab.engine.start_matlab()

        # PyQt layout and widget setup
        self.setMinimumSize(900, 900)
        self.mainlayout = QVBoxLayout()
        self.layout1 = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        fnt = QFont('Open Sans', 40, QFont.Bold)
        self.setWindowTitle('Live Robot Control')

        # add push buttons and text labels
        self.start_button = QPushButton('Start Test')
        self.stop_button = QPushButton('Stop Test')
        self.start_button.setFont(QFont('Open Sans', 16))
        self.stop_button.setFont(QFont('Open Sans', 16))
        self.start_button.setFixedSize(200, 50)
        self.stop_button.setFixedSize(200, 50)
        self.lbl = QLabel()
        self.lbltext = QLabel()
        self.lbl.setAlignment(Qt.AlignHCenter)
        self.lbltext.setAlignment(Qt.AlignHCenter)
        self.lbl.setFont(fnt)
        self.lbltext.setFont(fnt)

        # add buttons and text labels to the mainlayout
        self.layout1.addWidget(self.lbl)
        self.layout1.addWidget(self.lbltext)
        self.layout1.addStretch(1)
        self.mainlayout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        self.mainlayout.addWidget(self.stop_button, alignment=Qt.AlignCenter)
        self.mainlayout.addLayout(self.layout1)
        self.setLayout(self.mainlayout)

        # push button setup
        self.stop_button.hide()
        self.start_button.clicked.connect(self.start_stream_button)
        self.stop_button.clicked.connect(self.stop_stream_button)

        # set variables
        self.rawdata = "live_raw_data.txt"
        self.run = True
        self.show_stim=False
        self.data = []
        self.temp_result = 0
        self.frequency = 1000  # set frequency to 2500 Hertz
        self.duration = 500  # set duration to 1000 ms == 1 second
        # self.instructions()
        # self.savedata()

    # def instructions(self):
    #     self.lbltext.setText("Instructions:\n Think about moving your right arm to move the robot\nPress Enter to start")
    #     # have this stuff in start push button
    #     self.start = True
    #     self.arm_run = False
    #     #self.lbltext.setVisible(True)
    #
    # def keyPressEvent(self, event):
    #     # have this in start push button
    #     if self.start == True and self.arm_run == False and event.key() == Qt.Key_Return:
    #         #self.lbltext.clear(
    #         self.timer = QTimer()
    #         self.timer.timeout.connect(self.savedata)  # execute `display_time`
    #         self.timer.setInterval(1000)  # 1000ms = 1s
    #         self.timer.start()

    def start_stream_button(self):
        self.start = True
        self.arm_run = False
        self.start_button.hide()
        self.stop_button.show()
        self.lbltext.setText("Imagine grabing the circle to move the robot\nRelax to keep the robot still\nPromts will appear on the screen")
        self.data = []
        self.board = BoardShim(self.board_id, self.params)
        self.board.prepare_session()
        self.hardware_connected = True
        self.board.start_stream()
        self.timer = QTimer()
        self.timer.timeout.connect(self.savedata)  # execute `savedata`
        self.timer.setInterval(1000)  # 1000ms = 1s
        self.timer.start()
        
        

    # def movement(self):
    #     self.lbltext.setText('move your right hand\nuntill timer stops')

    def savedata(self):
        self.update()
        if self.run==True and self.arm_run==False:
            winsound.Beep(self.frequency, self.duration)
            self.show_stim=True
            self.control_shown= random.randrange(0,1)
            
            loop = QEventLoop()
            QTimer.singleShot(5000, loop.quit)
            loop.exec_()

            # get data from the board and write it to a file specified earlier
            self.data = self.board.get_board_data()
            DataFilter.write_file(self.data, self.rawdata, 'w')
           

            # Matlab feature extraction
            data_txtfile = r"live_raw_data.txt"
            bp_result, rms_result, bp_vals, rms_vals = self.m.bp_rms_extraction(data_txtfile, 1, nargout=4)
            rms_result = str(int(rms_result))
            bp_result = str(int(bp_result))
            bp_vals = list(bp_vals[0])
            rms_vals = list(rms_vals[0])
            self.bp_write_array=np.array(bp_result)
            self.bp_write_array.a

            # a = []
            # a.append(rms_result)
            # rms_result = a
            # print(a)
            # rms_vals = np.array(rms_vals)
            print("RMS values", rms_vals)
            print("bp values", bp_vals)

            # RMS classification
            # rms_result = self.m.RMS_classification(rms_vals)
            # rms_result = list(rms_result[0])
            print("RMS classification:", rms_result)
            print("bp classification:", bp_result)

        # bandpower classification
            # bp_result = self.m.RMS_classification(bp_vals)
            # bp_result = list(bp_result[0])

            #compare classification results
            if bp_result == rms_result:
                self.arm_out = rms_result
            elif rms_result==self.temp_result:
                self.arm_out==rms_result
            else:
                self.arm_out = self.temp_result

            # set the arm command to the RMS result and call the write_classification method
            #self.arm_out = rms_result
            self.write_classification()
            self.arm_run = True

            # call the arm_control method
            self.arm_control()
            
            self.run = True
            self.start = True

    def save_results(self):
        # open a text file to append the arry too
        write_array=np.array(se)
        with open('Live_data/bp_results.txt', 'wb') as f:
            np.savetxt(f, np.arange(3), fmt='%5d', delimiter=',')

        with open('Live_data/rms_results.txt', 'wb') as f:
             f.write('\n')

    def arm_control(self): #funtion to sent data to arm and conroll
        kanova()
        self.arm_run = False
        #print('arm_control', self.start, self.arm_run)

    def write_classification(self): # function to write classifacation data to file for arm to process
        # open the classification file in write mode
        with open('Live_data/classification.txt', 'w') as f:
            f.write(str(self.arm_out))

    def stop_stream_button(self): # function called by stop bttn
        self.run = False
        self.board.stop_stream()
        self.board.release_session()
        print('Stopped EEG stream.')

    def closeEvent(self, event): # call on closing the window
        #method called by closeing window
        self.run = False
        self.board.stop_stream()
        self.board.release_session()
        print('Stopped EEG stream')

    def paintEvent(self,event): # function to draw on screan
        # here is where we draw stuff on the screen
        # you give drawing instructions in pixels - here I'm getting pixel values based on window size
        print("paint event runs")
        painter = QPainter(self)
        if self.show_stim:
            print('Painting stim')
            painter.setBrush(QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern))
            cross_width = 100
            line_width = 20
            radius = 80
            center = self.geometry().width()//2
            offset = 100

            # check if count is zero; this removes the slight overlap when the cross should be gone
            if  self.control_shown== 0:
                self.setStyleSheet("background-color: red;")
                self.lbltext.setText("relax\ntry to not move the robot")

            # check if the count changed; if so, draw a new circle at a randomized position
            if (self.control_shown==1):
                self.setStyleSheet("background-color: green;")
                self.lbltext.setText("relax\ntry to not move the robot")
                # get position values (randomized) for one of four circles
                # draw two rectangles for the fixation cross
                painter.drawRect(center - cross_width//2, center - line_width//2, cross_width, line_width)
                painter.drawRect(center - line_width//2, center - cross_width//2, line_width, cross_width)

                # get position values radomized (Top Left and Top Right) at 4 locations
                rand_list = [center + offset - radius//2 + line_width*3, center - offset - radius//2 - line_width*3]
                xchoice = random.choice(rand_list) 
                #xchoice to extend the circles position along x-axis
                if xchoice == rand_list[0]:
                    xchoice += radius
                elif xchoice == rand_list[1]:
                    xchoice -= radius

                ychoice = rand_list[1]

                # choices match previous choices so change the x position choice
                if (xchoice == self.previous_xchoice) & (ychoice == self.previous_ychoice):
                    xchoice = random.choice([x for x in rand_list if x != self.previous_xchoice])
                # update previous values for the next loop
                self.previous_xchoice = xchoice
                self.previous_ychoice = ychoice
                # painting circle random a quadrent
                painter.drawEllipse(xchoice, ychoice, radius, radius)
        self.update()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mibaseline_win()
    main.show()
    sys.exit(app.exec())
