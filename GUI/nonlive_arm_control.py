import argparse
import time
from turtle import Turtle
import numpy as np
import pandas as pd
import sys
import csv

# PyQt5 GUI imports
from PyQt5 import QtCore, Qt
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, QTime, Qt, QEventLoop
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPainter, QBrush
from PyQt5 import QtGui
from PyQt5.QtOpenGL import *
from PyQt5 import QtCore, Qt
from PyQt5.Qt import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

# Matlab import
import matlab.engine
from short_movement import kanova


# class: Live Control Window
class nonlive(QWidget):
    def __init__(self):
        super().__init__()

        # initialize Matlab connection
        self.m = matlab.engine.start_matlab()

        # PyQt layout and widget setup
        self.setMinimumSize(900, 900)
        self.fnt = QFont('Open Sans', 20, QFont.Bold)
        self.setWindowTitle('Non-Live Robot Control')
        self.mainlayout = QVBoxLayout(self)
        self.layout1 = QVBoxLayout()

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
        self.lbl.setFont(self.fnt)
        self.lbltext.setFont(self.fnt)
        self.lbltext.setText("Press start to begin\nnon-live EEG data processing\nand classification for arm control.")
        self.lbltext.setVisible(True)

        # add buttons and text labels to the mainlayout
        self.layout1.addWidget(self.lbl)
        self.layout1.addWidget(self.lbltext)
        self.layout1.addStretch(1)
        self.mainlayout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        self.mainlayout.addWidget(self.stop_button, alignment=Qt.AlignCenter)

        # push button setup
        self.stop_button.hide()
        self.start_button.clicked.connect(self.classify_data)
        self.stop_button.clicked.connect(self.stop_button_function)

        # put layouts together
        self.mainlayout.addLayout(self.layout1)
        self.setLayout(self.mainlayout)

        # set variables and call function
        self.temp_result = 0
        self.arm_run = False
        self.run = True

    def classify_data(self):
        self.start_button.hide()
        self.stop_button.show()

        if self.run == True and self.arm_run == False:
            self.lbltext.setText("Non-Live EEG data processing\nand classification for arm control\nis being executed.\nPlease wait.")
            self.lbltext.setVisible(True)
            self.update()

            # Matlab feature extraction
            data_txtfile = r"alexis_nonlive_testing.txt"
            bp_result, rms_result, bp_vals, rms_vals = self.m.bp_rms_extraction(data_txtfile, 0, nargout=4)
            self.lbltext.setText("Non-Live EEG classification for\narm control is complete.")
            self.lbltext.setVisible(True)
            self.bp_result = bp_result[0]
            self.rms_result = rms_result[0]

            # set the arm command to the RMS result and call the write_classification method
            self.write_classification()
            self.arm_run = True

            # call the arm_control method
            self.arm_control()
            self.run = True
            self.start = True

    def arm_control(self):
        kanova()
        self.arm_run = False

    def write_classification(self):
        # open the classification file in write mode
        # change to write an array to file
        self.lbltext.setText("Classification results are being\nsent to the robotic arm.\n Please wait.")
        self.lbltext.setVisible(True)

        with open('Live_data/classification.txt', 'w') as f:
            for element in range(0, len(self.bp_result)):
                # compare classification results
                if self.bp_result[element] == self.rms_result[element]:
                    self.arm_out = self.rms_result[element]
                else:
                    self.arm_out = self.temp_result

                f.write(str(self.arm_out))

    def stop_button_function(self):
        self.run = False
        print('Stopped non-live arm control.')
        self.close()

    def closeEvent(self, event):
        self.run = False
        print('Stopped non-live arm control.')
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = nonlive()
    main.show()
    sys.exit(app.exec())

