# this is the main menu window, this is the start of the entire program.
# it allows the user to navigate to the test windows and live session windows.
# the user can decide to read files, simulate and livestream data from openbci hardware.
# the user can select the hardware they want to interface with: arduino, robot, simulation.

import sys
import numpy as np
import random
import time
import os
from PyQt5 import QtGui
from PyQt5.QtOpenGL import *
from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import *

from mi_window import mibaseline_win
from save_live_data import live
from live_graph_window import graph_win


class MenuWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        ####################################
        ##### Init Main Window Globals #####
        #################################### 

        '''
        -------------------INPUTS-------------------|    
        |                  TITLE                    |
        |       HARDWARE              TYPE          |
        |       MODEL                 PORT          |
        |       CSV/TXT                             |
        |                   LIMB                    |
        |------------------ACTIONS------------------|
        |                                           |
        |    IMPED       BASELINE        SESSION    |
        |    MI TEST     MODEL           RESULTS    |
        |                GRAPH                      |
        |                                           |
        |-------------------------------------------|

        '''
        
        # initialize window
        self.setMinimumSize(900, 900)
        self.setWindowTitle('Main Menu')
        
        # initialize layout
        self.layout = QGridLayout()
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        ### DEBUG ###
        self.debug = True

        if self.debug == True:
            self.bci_serial_port = 'COM1'
            # self.arduino_con = 'Debug'
            # self.arduino_serial_port = 'COM2'

        ###################################
        ### Initial GUI Input Elements ####
        ################################### 

        ### INITIAL INPUT LAYOUTS ###
        # create layouts explicitly for all GUI input fields
        self.title_layout = QHBoxLayout() 
        self.hardware_layout = QVBoxLayout()
        self.model_layout = QVBoxLayout()
        self.type_layout = QVBoxLayout()
        self.port_layout = QVBoxLayout()
        self.csv_layout = QVBoxLayout()
        #self.arduino_layout = QVBoxLayout()
        self.limb_layout = QVBoxLayout()

        '''
        |------------------INPUTS-------------------|    
        |                                           |
        |       HARDWARE              TYPE          |
        |       MODEL                 PORT          |
        |       CSV/TXT                             |
        |                   LIMB                    |
        |                                           |
        |-------------------------------------------|
        '''
        
        ### TITLE ###
        self.title = QLabel()
        self.title.setFont(QtGui.QFont('Arial',14))
        self.title.setText('Select hardware')
        self.title_layout.addWidget(self.title)
        
        ### HARDWARE ###
        # drop down menu to decide what hardware
        self.hardware_dropdown = QComboBox()
        self.hardware_dropdown.addItems(['openBCI'])
        self.hardware_dropdown.activated.connect(self.handle_hardware_choice)
        self.hardware_label = QLabel('Select hardware')
        self.hardware_layout.addWidget(self.hardware_label)
        self.hardware_layout.addWidget(self.hardware_dropdown)

        ### MODEL ###
        # drop down menu for model of hardware
        self.model_dropdown = QComboBox()
        self.model_label = QLabel('Select model')
        self.model_dropdown.setEnabled(False) # starts disabled
        self.model_dropdown.activated.connect(self.handle_model_choice)
        self.model_layout.addWidget(self.model_label)
        self.model_layout.addWidget(self.model_dropdown)

        ### CSV ###
        self.csv_name_edit = QLineEdit('eeg_log_file')
        self.csv_name_edit.returnPressed.connect(self.csv_name_changed)
        self.csv_name = 'eeg_log_file'
        self.csv_label = QLabel('CSV name to save to')
        self.csv_layout.addWidget(self.csv_label)
        self.csv_layout.addWidget(self.csv_name_edit)

        ### DATATYPE ###
        # drop down menu for simulate or live (previously included file step through)
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(['Task live', 'Task simulate'])
        self.type_dropdown.activated.connect(self.handle_type_choice)
        self.type_label = QLabel('Select data type')
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.type_dropdown)
        
        if self.debug == True:
            self.type_dropdown.setEnabled(True) # start enabled
        else:
            self.type_dropdown.setEnabled(False) # start disabled

        ### PORT ###
        self.openbci_label = QLabel("OpenBCI Serial Port")
        self.openbci_port = QLineEdit()
        self.openbci_port.setEnabled(False)
        self.port_layout.addWidget(self.openbci_label)
        self.port_layout.addWidget(self.openbci_port)
        self.openbci_port.setPlaceholderText("Enter Port # (Integers Only)") 
        self.openbci_port.textEdited.connect(self.handle_bci_port)

        ### LIMB ###
        self.limb_sub_layout = QHBoxLayout()
        self.limb_label = QLabel('Which arm is the target?')
        self.limb_rbtn1 = QRadioButton('Left Arm')
        self.limb_rbtn2 = QRadioButton('Right Arm')
        self.limb_rbtn1.toggled.connect(self.onClicked)
        self.limb_rbtn2.toggled.connect(self.onClicked)
        self.limb_sub_layout.addWidget(self.limb_rbtn1)
        self.limb_sub_layout.addWidget(self.limb_rbtn2)
        self.limb_layout.addWidget(self.limb_label)
        self.limb_layout.addLayout(self.limb_sub_layout)

        ### ADD INPUT SUBLAYOUTS TO MAIN ###
        self.layout.setContentsMargins(100, 100, 100, 100)
        self.hardware_layout.setContentsMargins(50, 50, 50, 50)
        self.model_layout.setContentsMargins(50, 50, 50, 50)
        self.csv_layout.setContentsMargins(50, 50, 50, 15)
        self.type_layout.setContentsMargins(50, 50, 50, 50)
        self.port_layout.setContentsMargins(50, 50, 50, 50)
        self.limb_layout.setContentsMargins(50, 15, 50, 25)
        self.layout.addLayout(self.title_layout, 0, 0, 1, -1, QtCore.Qt.AlignHCenter)
        self.layout.addLayout(self.hardware_layout, 1, 0)
        self.layout.addLayout(self.model_layout, 2, 0)
        self.layout.addLayout(self.csv_layout, 3, 0)
        self.layout.addLayout(self.type_layout, 1, 1)
        self.layout.addLayout(self.port_layout, 2, 1)
        self.layout.addLayout(self.limb_layout, 4, 0, 1, -1, QtCore.Qt.AlignHCenter)

        ####################################
        ##### Init GUI Action Elements #####
        ####################################

        '''
        |------------------ACTIONS------------------|
        |                                           |
        |    IMPED       BASELINE        SESSION    |
        |    ARDUINO     MODEL           RESULTS    |
        |                GRAPH                      |
        |-------------------------------------------|
        '''

        # here is a button to actually start a impedance window
        self.impedance_window_button = QPushButton('Impedance Check')
        self.impedance_window_button.setEnabled(False)
        self.layout.addWidget(self.impedance_window_button, 5, 0, 1, -1, QtCore.Qt.AlignHCenter)
        self.impedance_window_button.clicked.connect(self.open_impedance_window)

        # here is a button to actually start a motor imagery test window
        self.mi_window_button = QPushButton('Motor Imagery Baseline')
        self.mi_window_button.setEnabled(False)
        self.layout.addWidget(self.mi_window_button, 6, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.mi_window_button.clicked.connect(self.open_mi_window)

        # here is a button to actually start a live movement window
        self.live_window_button = QPushButton('Arm control')
        self.live_window_button.setEnabled(False)
        self.layout.addWidget(self.live_window_button, 7, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.live_window_button.clicked.connect(self.open_live_control)

        # here is a button to actually start a data window
        self.baseline_window_button = QPushButton('Oddball Baseline')
        self.baseline_window_button.setEnabled(False)
        self.layout.addWidget(self.baseline_window_button, 5, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.baseline_window_button.clicked.connect(self.open_baseline_window)

        # here is a button to train the model
        self.model_window_button = QPushButton('Train Model')
        self.model_window_button.setEnabled(True) # set to false for deployment
        self.layout.addWidget(self.model_window_button, 6, 0, 1, -1, QtCore.Qt.AlignHCenter)
        self.model_window_button.clicked.connect(self.open_model_window)

        # here is a button to start the session
        self.session_window_button = QPushButton('Start Session')
        if self.debug == True:
            self.session_window_button.setEnabled(True)
        else:
            self.session_window_button.setEnabled(False)
        self.layout.addWidget(self.session_window_button, 5, 1, 1, -1, QtCore.Qt.AlignHCenter)
        self.session_window_button.clicked.connect(self.open_session_window)

        # here is a button to display results of the session
        self.results_window_button = QPushButton('Results')
        self.results_window_button.setEnabled(False)
        self.layout.addWidget(self.results_window_button, 6, 1, 1, -1, QtCore.Qt.AlignHCenter)
        self.results_window_button.clicked.connect(self.open_results_window)

        # here is a button to display graph
        self.graph_window_button = QPushButton('Graph')
        self.graph_window_button.setEnabled(True)
        self.layout.addWidget(self.graph_window_button, 7, 0, 1, -1, QtCore.Qt.AlignHCenter)
        self.graph_window_button.clicked.connect(self.open_graph_window)

        # initialize variables
        self.data_window_open = False # data window open
        self.impedance_window_open = False # impedance window open
        self.mi_window_open = False # motor imagery test window open
        self.csv_name = None # save temp .csv name
        self.ml_model = None # initialize model variables
        self.targ_limb = None # target limb

        if self.debug == True:
            self.hardware = 'openBCI' 
            self.model = 'Cyton-Daisy'
            self.data_type = 'Task simulate'
            self.targ_limb = 1
            self.csv_name = 'eeg_log_file_'

    def closeEvent(self, event):
        # this code will autorun just before the window closes
        # we will check whether streams are running, if they are we will close them
        if self.data_window_open:
            self.data_window.close()
        event.accept()

    #########################################
    ##### Functions for Handling Inputs #####
    #########################################  

    def handle_hardware_choice(self):
        self.hardware = self.hardware_dropdown.currentText()
        # handle the choice of hardware - by opening up model selection
        self.model_dropdown.setEnabled(True)
        self.type_dropdown.setEnabled(False)
        self.type_dropdown.setCurrentIndex(-1)
        self.title.setText('Select model')
        self.model_dropdown.clear()
        if self.hardware_dropdown.currentText() == 'openBCI':
            self.model_dropdown.addItems(['Ganglion', 'Cyton', 'Cyton-Daisy'])
    
    def handle_model_choice(self):
        # handle the choice of model by opening up data type selection
        self.model = self.model_dropdown.currentText()
        self.baseline_window_button.setEnabled(False)
        self.openbci_port.setEnabled(False)
        self.type_dropdown.setEnabled(True)
        self.type_dropdown.setCurrentIndex(-1)
        self.title.setText('Select data type')

    def csv_name_changed(self):
        # this runs when the user hits enter on the text edit to set the name of the csv log file
        # first we check if file already exists
        print('Text is {}'.format(self.csv_name_edit.text()))
        if not self.csv_name_edit.text().endswith('.csv'):
            # add .csv ending if absent
            self.csv_name_edit.setText(self.csv_name_edit.text() + '.csv')
        print('CSV name after adding ending {}'.format(self.csv_name_edit.text()))
        
        if os.path.isfile(self.csv_name_edit.text()):
            # chop off .csv ending, add number, read .csv
            self.csv_name = self.csv_name_edit.text()[:-4] + '_1.csv'
        else:
            self.csv_name = self.csv_name_edit.text()

    def handle_type_choice(self):
        # handle the choice of data type
        self.data_type = self.type_dropdown.currentText()
        if self.data_type == 'Task live':
            self.title.setText('Select BCI Hardware Port')
            self.openbci_port.setEnabled(True)
        elif self.data_type == 'Task simulate':
            self.baseline_window_button.setEnabled(True)
            self.impedance_window_button.setEnabled(True)
            self.mi_window_button.setEnabled(True)
            self.live_window_button.setEnabled(True)
            self.title.setText('Check Impedance, Start Baseline or Motor Imagery Test')
        
    def handle_bci_port(self):
        # check for correct value entering and enable type dropdown menu
        if self.openbci_port.text().isdigit():
            self.type_dropdown.setEnabled(True)
            self.bci_serial_port = "COM" + self.openbci_port.text()
            if self.data_type == 'Task live':
                self.baseline_window_button.setEnabled(True)
                self.impedance_window_button.setEnabled(True)
                self.mi_window_button.setEnabled(True)
                self.live_window_button.setEnabled(True)
            self.title.setText('Check Impedance or Start Baseline')
        else:
            self.baseline_window_button.setEnabled(False)
            self.title.setText('Select BCI Hardware Port')

    def onClicked(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            if radioBtn.text() == 'Left Arm':
                self.targ_limb = 1
        elif radioBtn.text() == 'Right Arm':
            self.targ_limb = 2

    #########################################
    ##### Functions for Opening Windows #####
    #########################################    
    
    def open_mi_window(self):
        self.mi_window = mibaseline_win(
        parent = self,
        hardware = self.hardware, 
        model = self.model, 
        data_type = self.data_type,
        csv_name = self.csv_name, 
        serial_port = self.bci_serial_port,
        )   
        self.mi_window.show()
        self.is_mi_window_open = True
    
    def open_impedance_window(self):
        self.impedance_window = impedance_win(
        parent = self,
        hardware = self.hardware, 
        model = self.model, 
        data_type = self.data_type, 
        serial_port = self.bci_serial_port,
        )   
        self.impedance_window.show()
        self.is_impedance_window_open = True

    def open_baseline_window(self):
        self.data_window = baseline_win(
            hardware = self.hardware, 
            model = self.model,
            data_type = self.data_type, 
            csv_name = self.csv_name, 
            parent = self,
            serial_port = self.bci_serial_port,
            )
        self.data_window.show()
        self.is_data_window_open = True

    def open_model_window(self):
        self.impedance_window = model_win(
        parent = self,
        hardware = self.hardware, 
        model = self.model,
        targ_limb = self.targ_limb,
        )   
        self.impedance_window.show()
        self.is_impedance_window_open = True

    def open_session_window(self):
        self.session_window = session_win(
            hardware = self.hardware, 
            model = self.model,
            targ_limb = self.targ_limb,
            data_type = self.data_type, 
            csv_name = self.csv_name, 
            parent = self,
            serial_port = self.bci_serial_port,
            )
        self.session_window.show()
        self.is_session_window_open = True

    def open_results_window(self):
        self.session_window = session_win(
            hardware = self.hardware, 
            model = self.model,
            data_type = self.data_type, 
            csv_name = self.csv_name, 
            parent = self,
            serial_port = self.bci_serial_port,
            )
        self.session_window.show()
        self.is_session_window_open = True

    def open_graph_window(self):
        self.live_graph_window = graph_win(
        parent = self,
        hardware = self.hardware, 
        model = self.model, 
        data_type = self.data_type, 
        serial_port = self.bci_serial_port,
        )   
        self.live_graph_window.show()
        self.is_graph_window_open = True

    def open_live_control(self):
        self.live_win = live(
        parent = self,
        hardware = self.hardware, 
        model = self.model, 
        data_type = self.data_type, 
        serial_port = self.bci_serial_port,
        )   
        self.live_win.show()
        self.is_live_window_open = True

if __name__ == '__main__':    
    app = QApplication(sys.argv)    
    win = MenuWindow() 
    win.show() 
    sys.exit(app.exec())
