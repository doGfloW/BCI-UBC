from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
from PyQt5 import QtGui
from PyQt5.QtOpenGL import *
from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

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
        self.gridLayout.addWidget(self.graphWidget2, 0, 1)

        self.graphWidget3 = pg.PlotWidget()
        self.graphWidget3.setTitle('Channel 3', **styles)
        self.graphWidget3.setLabel('left', 'Amplitude', **styles)
        self.graphWidget3.setLabel('bottom', 'Time', **styles)
        self.graphWidget3.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget3, 1, 0)

        self.graphWidget4 = pg.PlotWidget()
        self.graphWidget4.setTitle('Channel 4', **styles)
        self.graphWidget4.setLabel('left', 'Amplitude', **styles)
        self.graphWidget4.setLabel('bottom', 'Time', **styles)
        self.graphWidget4.setBackground('w')
        self.gridLayout.addWidget(self.graphWidget4, 1, 1)

        self.x = list(range(100))  # 100 time points
        self.y = [randint(0, 100) for _ in range(100)]  # 100 data points

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line1 = self.graphWidget1.plot(self.x, self.y, pen=pen)
        self.data_line2 = self.graphWidget2.plot(self.x, self.y, pen=pen)
        self.data_line3 = self.graphWidget3.plot(self.x, self.y, pen=pen)
        self.data_line4 = self.graphWidget4.plot(self.x, self.y, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        if self.button1.isChecked():
            self.x = self.x[1:]  # Remove the first y element.
            self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
            self.y = self.y[1:]  # Remove the first
            self.y.append(randint(0, 100))  # Add a new random value.
            self.data_line1.setData(self.x, self.y)  # Update the data.

        if self.button2.isChecked():
            self.x = self.x[1:]  # Remove the first y element.
            self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
            self.y = self.y[1:]  # Remove the first
            self.y.append(randint(0, 100))  # Add a new random value.
            self.data_line2.setData(self.x, self.y)  # Update the data.

        if self.button3.isChecked():
            self.x = self.x[1:]  # Remove the first y element.
            self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
            self.y = self.y[1:]  # Remove the first
            self.y.append(randint(0, 100))  # Add a new random value.
            self.data_line3.setData(self.x, self.y)  # Update the data.

        if self.button4.isChecked():
            self.x = self.x[1:]  # Remove the first y element.
            self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
            self.y = self.y[1:]  # Remove the first
            self.y.append(randint(0, 100))  # Add a new random value.
            self.data_line4.setData(self.x, self.y)  # Update the data.


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
