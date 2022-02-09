#This is our Motor Imagery Test - Version 1
import sys
import csv
import random
from PyQt5.QtCore import QTimer, QTime, Qt, QEventLoop
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel,QWidget
from PyQt5.QtGui import QFont
import time
import winsound
import os.path
import numpy as np
DURATION_INT = 40
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes

SIMULATE = 0
FILE = 1
LIVESTREAM = 2

class mibaseline_win(QWidget):
    def __init__(self, hardware=None, model=None, sim_type=None, \
                 data_type=None, csv_name=None, parent=None,
                 arduino_port=None, serial_port=None):
        super().__init__()
        self.parent = parent
        self.sim_type = sim_type
        self.hardware = hardware
        self.model = model
        self.file_path= os.getcwd()+"\\GUI\\Baseline_tests"
        #print('save path: '+ self.file_path)
        timestamp = time.strftime("%Y%m%d-%H%M")
        self.csv_name =os.path.join( self.file_path ,csv_name[:-4] + '_' + timestamp + ".txt")
        # Brainflow Initialization
        self.params = BrainFlowInputParams()
        self.params.serial_port = serial_port
        # self.params.serial_port = 'COM15'

        self.data = []

        # BoardShim.enable_dev_board_logger()
        # add more jabronis
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

        self.resize(500, 500)

        layout = QVBoxLayout()
        self.setWindowTitle('Motor imergy baseline Test')
        fnt = QFont('Open Sans', 40, QFont.Bold)
        self.lbl = QLabel()
        self.lbltext=QLabel()
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setFont(fnt)
        self.lbltext.setFont(QFont('Open Sans', 40, QFont.Bold))
        layout.addWidget(self.lbl)

        self.lbltext = QLabel()
        layout.addWidget(self.lbltext)
        self.lbltext.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        self.count=0
        self.stim_code=0
        self.start = False
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        self.show()

        self.stim_timer = QTimer()
        # making it a precision timer
        self.stim_timer.setTimerType(0)
        self.stim_timer.setSingleShot(True)
        # setting the function to call when it times out
        # IMPORTANT: to change the function it calls, must first use timer.disconnect() to remove the previous one
        # otherwise will call both new and old fucntions
        self.stim_timer.timeout.connect(self.end_stim)
        self.end_trig=11
        self.frequency = 1000  # Set Frequency To 2500 Hertz
        self.duration = 500  # Set Duration To 1000 ms == 1 second


        # defining what each trial is

        self.movement={'move': (1), 'still': (2)}


        # Innitilize number of trials
        self.total_trials = 10
        move_trials = self.total_trials // 2
        no_move_trials = self.total_trials - move_trials
        # temp variable to help setup array
        a=np.empty((10,))
        a[::2] =[self.movement['move']] * move_trials
        a[1::2] = [self.movement['still']] * no_move_trials
        self.trials=a
        print(self.trials)
        self.curr_trial = 0
        # this is whether or not we've gone through all our trials yet
        self.finished = False
        self.show_stim = False
        # now we display the instructions
        self.running_trial = False
        # To ensure we dont try to close the object a second time
        self.is_end = False

        # Setting up the board
        self.board = BoardShim(self.board_id, self.params)
        self.board.prepare_session()
        print('init hardware is running with hardware', self.hardware, 'model', self.model)
        self.board.start_stream()
        self.hardware_connected = True


        # displaying the instructions
        self.instructions()

    # Method for showing the time
    def showTime(self):
        # checking if flag is true
        if self.start:
            # incrementing the counter
            self.count -= 1

            # timer is completed
            if self.count == 0:
                # making flag false
                self.start = False

                # setting text to the label
                self.arm_move=False
                self.stimulation()
                self.responding_time = True
                self.stim_timer.timeout.disconnect()
                self.stim_timer.timeout.connect(self.end_stim)
                self.stim_timer.start(1000)
                self.update()


        if self.start:
            # getting text from count
            text = str(self.count) + " s"

            # showing text
            self.lbl.setText(text)

    # Method for geting the time for the timer
    def get_seconds(self):

        # making flag false
        self.start = False

        # getting seconds and flag
        second=3
        done=True
        # if flag is true
        if done:
            # changing the value of count
            self.count = second
            #inserting marker into data
            self.board.insert_marker(int(self.stim_code))
            print("marker: " + str(int(self.stim_code)))

            # setting text to the label
            self.lbl.setText(str(second) + " s")

    # Method for starting the timer
    def start_action(self):
        self.get_seconds()
        # making flag true
        self.start = True


        # count = 0
        if self.count == 0:
            self.start = False
        self.update()




# method for Key event
    def keyPressEvent(self, event):
            if self.start == False and event.key() == Qt.Key_Return:
                self.lbltext.clear()
                #self.call_timer3()
                #self.movement()
                self.start_trial()

    # def movement(self):
    #     self.lbltext.setText('move your right hand\nuntill timer stops')

# instructions to displace at the start
    def instructions(self):
        self.lbltext.setFont(QFont('Open Sans', 40, QFont.Bold))
        self.lbltext.setText("Instructiuons\nMove your hand when it says\nPress Enter to start")

    def start_trial(self):
        # starts trial - starts timers.
        print('starting trial')
        self.stimulation()
        self.running_trial = True
        # setting stim code based on value for current trial
        print(self.curr_trial)
        self.stim_code = self.trials[self.curr_trial]
        print(self.stim_code)
        #time.sleep(0.5)
        print("curr: " + str(self.curr_trial) + " < " + str(self.total_trials))
        if self.curr_trial < self.total_trials - 1:
            self.curr_trial += 1
            self.start_action()
            winsound.Beep(self.frequency, self.duration)
        else:
            print('all trials done')
            self.finished = True
            self.board.insert_marker(self.end_trig)
            self.on_end()

    def end_stim(self):
        print('ending stimulation')
        self.responding_time = False
        self.show_stim = False
        self.board.insert_marker(self.end_trig)
        print("End marker: " +str(self.end_trig))
        # self.data = self.board.get_board_data()
        self.update()
        # time.sleep(1)

        self.stim_timer.timeout.disconnect()
        self.stim_timer.timeout.connect(self.start_trial)

        self.stim_timer.start(1000)

    def stimulation(self):
        a=int(self.stim_code)

        if self.curr_trial==0:
            self.lbl.setText("Starting in 3,2,1")
            loop = QEventLoop()
            QTimer.singleShot(3000, loop.quit)
            loop.exec_()
            self.lbltext.setText('move your right hand\nuntill timer stops')
            self.setStyleSheet("background-color: green;")
        if  self.running_trial==True and a==1:
            self.lbl.setText("Stop!!\nKeep arm still")
            loop = QEventLoop()
            QTimer.singleShot(500, loop.quit)
            loop.exec_()
            self.lbltext.setText('Keep arm still\nuntill timer stops')
            self.setStyleSheet("background-color: cyan;")
        if  self.running_trial==True and a==2:
            self.lbl.setText("Begin moving!!\nDont stop moving arm")
            loop = QEventLoop()
            QTimer.singleShot(500, loop.quit)
            loop.exec_()
            self.lbltext.setText('move your right hand\nuntill timer stops')
            self.setStyleSheet("background-color: green;")

    def on_end(self):
        # called by end timer
        print('stop eeg stream ran')

        self.data = self.board.get_board_data()

        self.board.stop_stream()
        self.board.release_session()

        DataFilter.write_file(self.data, self.csv_name, 'w')
        print('EEG data saved')
        # self.is_end = True

        # let's initialize electrode to display
        self.curr_electrode = 0
        # and now start up erp graphing!

        # erp graphing is unused
        ###############################
        # self.display_erp()

        self.close()

    # Method for starting the eeg data stream
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
