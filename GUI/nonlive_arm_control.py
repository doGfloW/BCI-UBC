import argparse
import time
from turtle import Turtle
import numpy as np
import pandas as pd
import sys
import csv

# PyQt5 GUI imports
from PyQt5 import QtCore, Qt
from PyQt5.QtCore import QTimer, QTime, Qt, QEventLoop
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPainter, QBrush

# Matlab import
import matlab.engine
from short_movement import kanova


# class: Live Control Window
class nonlive():
    def __init__(self):
        super().__init__()

        # initialize Matlab connection
        self.m = matlab.engine.start_matlab()
        self.temp_result = 0
        self.classify_data()

    def classify_data(self):
        if self.arm_run == False:
            # Matlab feature extraction
            data_txtfile = r"alexis_nonlive_testing.txt"
            bp_result, rms_result, bp_vals, rms_vals = self.m.bp_rms_extraction(data_txtfile, 0, nargout=4)

            self.bp_result = bp_result[0]
            self.rms_result = rms_result[0]

            print("BP classification", self.bp_result)
            print("RMS classification", self.rms_result)

            # set the arm command to the RMS result and call the write_classification method
            self.write_classification()
            self.arm_run = True

            # call the arm_control method
            self.arm_control()
            self.start = True

    def arm_control(self):
        kanova()
        self.arm_run = False

    def write_classification(self):
        # open the classification file in write mode
        # change to write an array to file
        with open('Live_data/classification.txt', 'w') as f:
            for element in range(0, len(self.bp_result)):
                # compare classification results
                if self.bp_result[element] == self.rms_result[element]:
                    self.arm_out = self.rms_result[element]
                else:
                    self.arm_out = self.temp_result

                f.write(str(self.arm_out))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    sys.exit(app.exec())
