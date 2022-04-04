# Motor Imagery Test - Version 1

# functionality imports
import sys
import csv
import random

# PyQt5 GUI imports
from PyQt5 import QtCore, Qt
from PyQt5.QtCore import QTimer, QTime, Qt, QEventLoop
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel,QWidget, QHBoxLayout
from PyQt5.QtGui import QFont, QPainter, QBrush

# computation imports
import time
import winsound
import os.path
import numpy as np

# Brainflow imports
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes

# program constants
DURATION_INT = 40
SIMULATE = 0
FILE = 1
LIVESTREAM = 2


# class: Motor Imagery Window
class mibaseline_win(QWidget):
    def __init__(self, hardware=None, model=None, sim_type=None,
                 data_type=None, csv_name=None, parent=None,
                 arduino_port=None, serial_port=None):
        super().__init__()
        self.parent = parent
        self.sim_type = sim_type
        self.hardware = hardware
        self.model = model
        
        self.file_path = os.getcwd() + "\\Baseline_tests"
        # print('save path: '+ self.file_path)
        timestamp = time.strftime("%Y%m%d-%H%M")
        self.csv_name = os.path.join( self.file_path ,csv_name[:-4] + '_' + timestamp + ".txt")
        #------------this is for a test: ----------self.csv_name_1 = self.csv_name =os.path.join( self.file_path ,csv_name + '_' + timestamp + ".txt")

        # Brainflow initialization
        self.params = BrainFlowInputParams()
        self.params.serial_port = serial_port
        # self.params.serial_port = 'COM15'

        self.data = []

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

        # PyQt window basic layout
        self.setMinimumSize(900, 900)
        self.mainlayout = QVBoxLayout()
        self.layout1 = QVBoxLayout()
        fnt = QFont('Open Sans', 40, QFont.Bold)
        self.setWindowTitle('Motor Imagery Baseline Test')

        # add text labels
        self.lbl = QLabel()
        self.lbltext = QLabel()
        self.lbl.setAlignment(Qt.AlignHCenter)
        self.lbltext.setAlignment(Qt.AlignHCenter)
        self.lbl.setFont(fnt)
        self.lbltext.setFont(fnt)

        # add text labels to the main layout
        self.layout1.addWidget(self.lbl)
        self.layout1.addWidget(self.lbltext)
        self.layout1.addStretch(1)
        self.mainlayout.addLayout(self.layout1)
        self.setLayout(self.mainlayout)
        # self.setLayout(self.layout2)

        # set previous values for the random circles
        self.previous_count = 0
        self.previous_xchoice = 0
        self.previous_ychoice = 0

        # start the timer
        self.start = False
        self.count = 0
        self.stim_code = 0
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        self.show()

        # make it a precision timer
        self.stim_timer = QTimer()
        self.stim_timer.setTimerType(0)
        self.stim_timer.setSingleShot(True)
        
        # setting the function to call when it times out
        # IMPORTANT: to change the function it calls, 
        # must first use timer.disconnect() to remove the previous one
        # otherwise will call both new and old fucntions
        self.stim_timer.timeout.connect(self.end_stim)
        
        self.end_trig = 11  # end of period marker value
        self.frequency = 1000  # set frequency to 2500 Hertz
        self.duration = 500  # set duration to 1000 ms == 1 second

        # action periods per trial
        self.movement = {'move': 1, 'still': 2}

        # initialize number of trials
        self.total_trials = 10
        move_trials = self.total_trials // 2
        no_move_trials = self.total_trials - move_trials

        # temp variable to help setup array
        a = np.empty((10,))
        a[::2] = [self.movement['move']] * move_trials
        a[1::2] = [self.movement['still']] * no_move_trials
        self.trials = a
        print('trial', self.trials)
        self.curr_trial = 0

        # this is whether or not we've gone through all our trials yet
        self.finished = False
        self.show_stim = False

        # ensure we dont try to close the object a second time
        self.running_trial = False
        self.is_end = False

        # setting up the board
        self.board = BoardShim(self.board_id, self.params)
        self.board.prepare_session()
        print('Init hardware is running with hardware', self.hardware, 'model', self.model)
        self.board.start_stream()
        self.hardware_connected = True

        # display the instructions
        self.instructions()

    """ Functions for Test Program """

    # method for showing the time
    def showTime(self):
        # check if flag is true
        if self.start:
            # countdown timer; increment the counter
            self.count -= 1
            self.update()

            # timer is completed
            if self.count == 0:
                # make flag false
                self.start = False

                # set text to the label
                self.stimulation()
                self.responding_time = True
                self.stim_timer.timeout.disconnect()
                self.stim_timer.timeout.connect(self.end_stim)
                self.stim_timer.start(1000)
                self.update()

        if self.start:
            # get text from count and show text
            text = str(self.count) + " s"
            self.lbl.setText(text)

    # method for geting the time for the timer
    def get_seconds(self):
        # make flag false
        self.start = False

        # get seconds and flag
        second = 10
        done = True

        if done:
            # change the count value
            self.count = second

            #insert marker into the data
            self.board.insert_marker(int(self.stim_code))
            print("marker: " + str(int(self.stim_code)))

            # set text to the label
            self.lbl.setText(str(second) + " s")

    # method for starting the timer
    def start_action(self):
        self.get_seconds()

        # make flag true
        self.start = True

        # check if the count is 0
        if self.count == 0:
            self.start = False

        self.update()

    # method for key event
    def keyPressEvent(self, event):
        if self.start == False and event.key() == Qt.Key_Return:
            self.lbltext.clear()
            # self.call_timer3()
            # self.movement()
            self.start_trial()

    # def movement(self):
    #     self.lbltext.setText('move your right hand\nuntill timer stops')

    # method to display instructions at the start
    def instructions(self):
        self.lbltext.setText("Instructions:\nMove your hand when it says\nPress Enter to start")
        # self.lbltext.setVisible(True)
        
    def start_trial(self):
        # starts trial - starts timers
        print('Starting trial')
        self.stimulation()
        self.running_trial = True

        # setting stim code based on value for current trial
        print(self.curr_trial)
        self.stim_code = self.trials[self.curr_trial]
        print(self.stim_code)
        # time.sleep(0.5)
        print("Curr: " + str(self.curr_trial) + " < " + str(self.total_trials))

        if self.curr_trial < self.total_trials - 1:
            self.curr_trial += 1
            #self.show_stim=True
            self.start_action()
            winsound.Beep(self.frequency, self.duration)
        else:
            print('All trials done')
            self.finished = True
            self.board.insert_marker(self.end_trig)
            self.on_end()

    def end_stim(self):
        print('Ending stimulation')
        self.responding_time = False
        self.show_stim = False
        self.board.insert_marker(self.end_trig)
        print("End marker: " + str(self.end_trig))
        self.update()
        # self.data = self.board.get_board_data()
        # time.sleep(1)
        self.stim_timer.timeout.disconnect()
        self.stim_timer.timeout.connect(self.start_trial)
        self.stim_timer.start(1000)

    def stimulation(self):
        a = int(self.stim_code)

        if self.curr_trial == 0:
            self.lbl.setText("Starting in 3,2,1")
            loop = QEventLoop()
            QTimer.singleShot(3000, loop.quit)
            loop.exec_()
            self.lbltext.setText('Imagine grabbing the circle')
            self.setStyleSheet("background-color: green;")
            self.show_stim = True
        
        if self.running_trial == True and a == 1:
            self.lbl.setText("Relax")
            self.lbltext.clear()
            self.show_stim = False
            loop = QEventLoop()
            QTimer.singleShot(500, loop.quit)
            loop.exec_()
            self.lbltext.setText('Imagine your arm is still\nuntil timer stops')
            self.setStyleSheet("background-color: red;")
        
        if self.running_trial == True and a == 2:
            self.lbl.setText("Move")
            self.lbltext.clear()
            self.show_stim = True
            loop = QEventLoop()
            QTimer.singleShot(500, loop.quit)
            loop.exec_()
            self.lbltext.setText('Imagine grabbing the circle')
            self.setStyleSheet("background-color: green;")

    def paintEvent(self, event):
        # here is where we draw stuff on the screen
        # you give drawing instructions in pixels - here I'm getting pixel values based on window size
        # print('Paint event runs')
        painter = QPainter(self)
        # print("Painter showing stim " + str(self.show_stim))

        if self.show_stim:
            # print('Painting stim')
            painter.setBrush(QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern))
            cross_width = 100
            line_width = 20
            radius = 80
            center = self.geometry().width()//2
            offset = 100

            # check if count is zero; this removes the slight overlap when the cross should be gone
            if self.count != 0:
                # draw two rectangles for the fixation cross
                painter.drawRect(center - cross_width//2, center - line_width//2, cross_width, line_width)
                painter.drawRect(center - line_width//2, center - cross_width//2, line_width, cross_width)

            # check if the count changed; if so, draw a new circle at a randomized position
            if (self.count != self.previous_count) & (self.count != 0):
                # get position values (randomized) for one of four circles
                # rand_list = [center + offset - radius//2, center - offset - radius//2]
                # xchoice = random.choice(rand_list)
                # ychoice = random.choice(rand_list)

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
                self.previous_count = self.count
                self.previous_xchoice = xchoice
                self.previous_ychoice = ychoice



                # painting circle random a quadrent
                painter.drawEllipse(xchoice, ychoice, radius, radius)

        elif self.finished:
            # no need to paint anything specifically
            pass

    def on_end(self):
        # called by end timer
        print('Stop EEG stream')

        self.data = self.board.get_board_data()
        self.board.stop_stream()
        self.board.release_session()
        DataFilter.write_file(self.data, self.csv_name, 'w')
        print('EEG data saved')
        # self.is_end = True

        # let's initialize electrode to display
        # self.curr_electrode = 0
        # and now start up erp graphing!

        # erp graphing is unused
        ###############################
        # self.display_erp()

        self.close()

    def closeEvent(self, event):
        # called by end timer
        self.run = False
        self.board.stop_stream()
        self.board.release_session()
        print('stop eeg stream ran')

    # method for starting the eeg data stream
    # def eeg_start(self):
    #     self.board = BoardShim(self.board_id, self.params)
    #     self.board.prepare_session()
    #     print('init hardware is running with hardware', self.hardware, 'model', self.model)
    #     self.board.start_stream()
    #     self.hardware_connected = True

    # def timer_Start3(self):
    #     self.time_left_int = 3
    #
    #     self.my_qtimer = QTimer(self)
    #     self.my_qtimer.timeout.connect(self.timer_3)
    #     self.my_qtimer.start(1000)
    #
    #     self.update_gui()
    #
    #
    # def timer_3(self):
    #     self.time_left_int -= 1
    #
    #     if self.time_left_int == 0:
    #         self.widget_counter_int = (self.widget_counter_int + 1) % 4
    #         self.lbl.setCurrentIndex(self.widget_counter_int)
    #         self.time_left_int = 3
    #         self.start=False
    #
    #     self.update_gui()

    # def call_timer(self):
    #     self.timer_start()
    #     self.update_gui()
    #
    # def call_timer3(self):
    #     self.lbl.setText("Starting in ..")
    #     loop = QEventLoop()
    #     QTimer.singleShot(1000, loop.quit)
    #     loop.exec_()
    #     self.timer_Start3()
    #     self.update_gui()

    # def timer_start(self):
    #     self.time_left_int = DURATION_INT
    #     self.update_gui()
    #
    #
    # def timer_timeout(self):
    #     self.time_left_int -= 1
    #
    #     if self.time_left_int == 0:
    #         self.widget_counter_int = (self.widget_counter_int + 1) % 4
    #         self.lbl.setCurrentIndex(self.widget_counter_int)
    #         self.time_left_int = DURATION_INT
    #
    #     self.update_gui()

    # def update_gui(self):
    #     self.lbl.setText(str(self.time_left_int))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mibaseline_win()
    main.show()
    sys.exit(app.exec())
