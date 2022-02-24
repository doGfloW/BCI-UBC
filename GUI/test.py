
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
from PyQt5 import QtGui
from PyQt5.QtOpenGL import *
from PyQt5 import QtCore, Qt
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
       

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        
        self.layout0 = QVBoxLayout()
        self.widget = QWidget()
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setLayout(self.layout0)
        self.button1 = QPushButton("Channel 1")
        self.button1.setFixedSize(120, 30) 
        self.button2 = QPushButton("Channel 2")
        self.button3 = QPushButton( "Channel 3")
        self.button4 = QPushButton( "Channel 4")
        self.layout0.addWidget(self.button1)

    
        self.x = list(range(100))  # 100 time points
        self.y = [randint(0,100) for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        styles = {'color':'r', 'font-size':'20px'}
        self.graphWidget.setLabel('left', 'Amplitude', **styles)
        self.graphWidget.setLabel('bottom', 'x', **styles)


       


    def update_plot_data(self):

        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append( randint(0,100))  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

