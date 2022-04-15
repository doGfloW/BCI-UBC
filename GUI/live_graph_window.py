import argparse
import logging
import os
import sys
import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5.QtOpenGL import *
from PyQt5 import QtCore, Qt
from PyQt5.Qt import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtGui import QFont
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from random import randint


class graph_win(QMainWindow):
    def __init__(self, hardware=None, model=None,
                 data_type=None, parent=None, serial_port=None):
        super(graph_win, self).__init__()
        # setting up the board
        self.params = BrainFlowInputParams()
        self.params.serial_port = serial_port
        self.board_id = 0
        self.board = BoardShim(self.board_id, self.params)
        self.board.prepare_session()
        self.board.start_stream()
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.update_speed_ms = 50
        self.window_size = 4
        self.num_points = self.window_size * self.sampling_rate

        # region Initial layout
        #styles = {'color': 'black', 'font-size': '16px'}
        self.setWindowTitle('Main Window')
        self.setGeometry(0, 0, 1500, 900)

        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        self.gridLayout = QGridLayout()
        self.vLayout.addLayout(self.hLayout)
        self.vLayout.addLayout(self.gridLayout)

        self.vLayout.setContentsMargins(10, 10, 10, 10)
        self.hLayout.setContentsMargins(10, 10, 10, 10)
        self.vLayout.setSpacing(10)
        self.hLayout.setSpacing(10)

        self.widget = QWidget()
        self.widget.setLayout(self.vLayout)
        self.setCentralWidget(self.widget)
        # endregion

        # region Buttons
        self.button1 = QPushButton('Channel 1')
        self.button2 = QPushButton('Channel 2')
        self.button3 = QPushButton('Channel 3')
        self.button4 = QPushButton('Channel 4')
        self.button5 = QPushButton('Channel 5')
        self.button6 = QPushButton('Channel 6')
        self.button7 = QPushButton('Channel 7')
        self.button8 = QPushButton('Channel 8')

        self.button1.setFixedSize(80, 30)
        self.button2.setFixedSize(80, 30)
        self.button3.setFixedSize(80, 30)
        self.button4.setFixedSize(80, 30)
        self.button5.setFixedSize(80, 30)
        self.button6.setFixedSize(80, 30)
        self.button7.setFixedSize(80, 30)
        self.button8.setFixedSize(80, 30)

        self.button1.setCheckable(True)
        self.button2.setCheckable(True)
        self.button3.setCheckable(True)
        self.button4.setCheckable(True)
        self.button5.setCheckable(True)
        self.button6.setCheckable(True)
        self.button7.setCheckable(True)
        self.button8.setCheckable(True)

        self.button1.clicked.connect(self.update_plot_data)
        self.button2.clicked.connect(self.update_plot_data)
        self.button3.clicked.connect(self.update_plot_data)
        self.button4.clicked.connect(self.update_plot_data)
        self.button5.clicked.connect(self.update_plot_data)
        self.button6.clicked.connect(self.update_plot_data)
        self.button7.clicked.connect(self.update_plot_data)
        self.button8.clicked.connect(self.update_plot_data)

        # self.button1.setStyleSheet("background-color : lightgrey")
        # self.button2.setStyleSheet("background-color : lightgrey")
        # self.button3.setStyleSheet("background-color : lightgrey")
        # self.button4.setStyleSheet("background-color : lightgrey")
        # self.button5.setStyleSheet("background-color : lightgrey")
        # self.button6.setStyleSheet("background-color : lightgrey")
        # self.button7.setStyleSheet("background-color : lightgrey")
        # self.button8.setStyleSheet("background-color : lightgrey")

        self.hLayout.addWidget(self.button1)
        self.hLayout.addWidget(self.button2)
        self.hLayout.addWidget(self.button3)
        self.hLayout.addWidget(self.button4)
        self.hLayout.addWidget(self.button5)
        self.hLayout.addWidget(self.button6)
        self.hLayout.addWidget(self.button7)
        self.hLayout.addWidget(self.button8)
        # endregion

        # region Graphs
        self.graphWidget1 = pg.PlotWidget()
        self.graphWidget1.setTitle('Channel 1')
        self.graphWidget1.setLabel('left', 'Amplitude')
        self.graphWidget1.setLabel('bottom', 'Time')
        self.graphWidget1.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget1, 0, 0)

        self.graphWidget2 = pg.PlotWidget()
        self.graphWidget2.setTitle('Channel 2')
        self.graphWidget2.setLabel('left', 'Amplitude')
        self.graphWidget2.setLabel('bottom', 'Time')
        self.graphWidget2.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget2, 1, 0)

        self.graphWidget3 = pg.PlotWidget()
        self.graphWidget3.setTitle('Channel 3')
        self.graphWidget3.setLabel('left', 'Amplitude')
        self.graphWidget3.setLabel('bottom', 'Time')
        self.graphWidget3.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget3, 2, 0)

        self.graphWidget4 = pg.PlotWidget()
        self.graphWidget4.setTitle('Channel 4')
        self.graphWidget4.setLabel('left', 'Amplitude')
        self.graphWidget4.setLabel('bottom', 'Time')
        self.graphWidget4.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget4, 3, 0)

        self.graphWidget5 = pg.PlotWidget()
        self.graphWidget5.setTitle('Channel 5')
        self.graphWidget5.setLabel('left', 'Amplitude')
        self.graphWidget5.setLabel('bottom', 'Time')
        self.graphWidget5.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget5, 4, 0)

        self.graphWidget6 = pg.PlotWidget()
        self.graphWidget6.setTitle('Channel 6')
        self.graphWidget6.setLabel('left', 'Amplitude')
        self.graphWidget6.setLabel('bottom', 'Time')
        self.graphWidget6.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget6, 5, 0)

        self.graphWidget7 = pg.PlotWidget()
        self.graphWidget7.setTitle('Channel 7')
        self.graphWidget7.setLabel('left', 'Amplitude')
        self.graphWidget7.setLabel('bottom', 'Time')
        self.graphWidget7.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget7, 6, 0)

        self.graphWidget8 = pg.PlotWidget()
        self.graphWidget8.setTitle('Channel 8')
        self.graphWidget8.setLabel('left', 'Amplitude')
        self.graphWidget8.setLabel('bottom', 'Time')
        self.graphWidget8.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget8, 7, 0)
        # endregion

        pen = pg.mkPen(color=(255, 0, 0))
        self.x = list(range(100))
        self.y = [0] * 100
        self.data_line1 = self.graphWidget1.plot(self.x, self.y, pen=pen)
        self.data_line2 = self.graphWidget2.plot(self.x, self.y, pen=pen)
        self.data_line3 = self.graphWidget3.plot(self.x, self.y, pen=pen)
        self.data_line4 = self.graphWidget4.plot(self.x, self.y, pen=pen)
        self.data_line5 = self.graphWidget5.plot(self.x, self.y, pen=pen)
        self.data_line6 = self.graphWidget6.plot(self.x, self.y, pen=pen)
        self.data_line7 = self.graphWidget7.plot(self.x, self.y, pen=pen)
        self.data_line8 = self.graphWidget8.plot(self.x, self.y, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        data = self.board.get_current_board_data(self.num_points)

        if self.button1.isChecked():
            pass
        else:
            # what does this do?
            # DataFilter.detrend(data[0], DetrendOperations.CONSTANT.value)
            # append for y? and which index is for channel 1?
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            # self.y = self.y[1:]
            # self.y.append(randint(0, 100))
            self.y = data[self.eeg_channels[0]].tolist()
            self.data_line1.setData(self.y)

        if self.button2.isChecked():
            pass
        else:
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            self.y = data[self.eeg_channels[1]].tolist()
            self.data_line2.setData(self.y)

        if self.button3.isChecked():
            pass
        else:
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            self.y = data[self.eeg_channels[2]].tolist()
            self.data_line3.setData(self.y)

        if self.button4.isChecked():
            pass
        else:
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            self.y = data[self.eeg_channels[3]].tolist()
            self.data_line4.setData(self.y)

        if self.button5.isChecked():
            pass
        else:
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            self.y = data[self.eeg_channels[4]].tolist()
            self.data_line5.setData(self.y)

        if self.button6.isChecked():
            pass
        else:
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            self.y = data[self.eeg_channels[5]].tolist()
            self.data_line6.setData(self.y)

        if self.button7.isChecked():
            pass
        else:
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            self.y = data[self.eeg_channels[6]].tolist()
            self.data_line7.setData(self.y)

        if self.button8.isChecked():
            pass
        else:
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            self.y = data[self.eeg_channels[7]].tolist()
            self.data_line8.setData(self.y)

        # self.app.processEvents()
    # def closeEvent(self, event):
    #         self.board.stop_stream()
    #         self.board.release_session()
    #         print('Stopped EEG stream')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = graph_win()
    main.show()
    sys.exit(app.exec())
