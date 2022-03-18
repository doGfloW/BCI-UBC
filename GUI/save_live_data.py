import argparse
import time
from xml.dom.pulldom import default_bufsize
import numpy as np
import pandas as pd
import sys

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
from PyQt5 import QtCore, Qt
from PyQt5.QtCore import QTimer, QTime, Qt, QEventLoop
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel,QWidget, QHBoxLayout
from PyQt5.QtGui import QFont, QPainter, QBrush

class win(QWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(900, 900)
        self.mainlayout=QVBoxLayout()
        self.layout1 = QVBoxLayout()
        fnt = QFont('Open Sans', 40, QFont.Bold)
        
        self.setWindowTitle('Motor imergy baseline Test')
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
        BoardShim.enable_dev_board_logger()

        # use synthetic board for demo
        params = BrainFlowInputParams()
        self.board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)
        self.board.prepare_session()
        self.board.start_stream()
        self.run=True
        self.data=[]
        self.savedata()
        self.board.stop_stream()
        self.board.release_session()



    def savedata (self):
        while self.run==True:
            self.data=[]
            time.sleep(1)
            self.data = self.board.get_board_data()
            DataFilter.write_file(self.data, 'eeg_data.txt', 'w')
            print("saved data")
            time.sleep(1)

    def on_end(self):
            # called by end timer
            self.run=False
            print('stop eeg stream ran')


if __name__ == "__main__":
   app = QApplication(sys.argv)
   main = win()
   main.show()
   sys.exit(app.exec())
