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


class MainWindow(QMainWindow):
    def __init__(self, board_shim, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.update_speed_ms = 50
        self.window_size = 4
        self.num_points = self.window_size * self.sampling_rate

        #region Initial layout
        styles = {'color': 'black', 'font-size': '16px'}
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
        #endregion

        #region Buttons
        self.button1 = QPushButton('Channel 1')
        self.button2 = QPushButton('Channel 2')
        self.button3 = QPushButton('Channel 3')
        self.button4 = QPushButton('Channel 4')

        self.button1.setFixedSize(80, 30)
        self.button2.setFixedSize(80, 30)
        self.button3.setFixedSize(80, 30)
        self.button4.setFixedSize(80, 30)

        self.button1.setCheckable(True)
        self.button2.setCheckable(True)
        self.button3.setCheckable(True)
        self.button4.setCheckable(True)

        self.button1.clicked.connect(self.update_plot_data)
        self.button2.clicked.connect(self.update_plot_data)
        self.button3.clicked.connect(self.update_plot_data)
        self.button4.clicked.connect(self.update_plot_data)

        self.button1.setStyleSheet("background-color : lightgrey")
        self.button2.setStyleSheet("background-color : lightgrey")
        self.button3.setStyleSheet("background-color : lightgrey")
        self.button4.setStyleSheet("background-color : lightgrey")

        self.hLayout.addWidget(self.button1)
        self.hLayout.addWidget(self.button2)
        self.hLayout.addWidget(self.button3)
        self.hLayout.addWidget(self.button4)
        #endregion

        #region Graphs
        self.graphWidget1 = pg.PlotWidget()
        self.graphWidget1.setTitle('Channel 1', **styles)
        self.graphWidget1.setLabel('left', 'Amplitude', **styles)
        self.graphWidget1.setLabel('bottom', 'Time', **styles)
        self.graphWidget1.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget1, 0, 0)

        self.graphWidget2 = pg.PlotWidget()
        self.graphWidget2.setTitle('Channel 2', **styles)
        self.graphWidget2.setLabel('left', 'Amplitude', **styles)
        self.graphWidget2.setLabel('bottom', 'Time', **styles)
        self.graphWidget2.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget2, 1, 0)

        self.graphWidget3 = pg.PlotWidget()
        self.graphWidget3.setTitle('Channel 3', **styles)
        self.graphWidget3.setLabel('left', 'Amplitude', **styles)
        self.graphWidget3.setLabel('bottom', 'Time', **styles)
        self.graphWidget3.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget3, 2, 0)

        self.graphWidget4 = pg.PlotWidget()
        self.graphWidget4.setTitle('Channel 4', **styles)
        self.graphWidget4.setLabel('left', 'Amplitude', **styles)
        self.graphWidget4.setLabel('bottom', 'Time', **styles)
        self.graphWidget4.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget4, 3, 0)
        #endregion

        pen = pg.mkPen(color=(255, 0, 0))
        self.x = list(range(100))
        self.y = [0] * 100
        self.data_line1 = self.graphWidget1.plot(self.x, self.y, pen=pen)
        self.data_line2 = self.graphWidget2.plot(self.x, self.y, pen=pen)
        self.data_line3 = self.graphWidget3.plot(self.x, self.y, pen=pen)
        self.data_line4 = self.graphWidget4.plot(self.x, self.y, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update(self):
        data = self.board_shim.get_current_board_data(self.num_points)

        if self.button1.isChecked():
            pass
        else:
            # what does this do?
            # DataFilter.detrend(data[0], DetrendOperations.CONSTANT.value)
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            # append for y? and which index is for channel 1?
            self.y = data[self.eeg_channels[0]].tolist()
            self.data_line1.setData(self.x, self.y)

        if self.button2.isChecked():
            pass
        else:
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            # append for y? and which index is for channel 2?
            self.y = data[self.eeg_channels[1]].tolist()
            self.data_line1.setData(self.x, self.y)

        if self.button3.isChecked():
            pass
        else:
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            # append for y? and which index is for channel 3?
            self.y = data[self.eeg_channels[2]].tolist()
            self.data_line1.setData(self.x, self.y)

        if self.button4.isChecked():
            pass
        else:
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            # append for y? and which index is for channel 4?
            self.y = data[self.eeg_channels[3]].tolist()
            self.data_line1.setData(self.x, self.y)

        self.app.processEvents()


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
