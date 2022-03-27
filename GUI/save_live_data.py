import argparse
import time
import numpy as np
import pandas as pd
import sys

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds



import matlab.engine

class win(QMainWindow):
    def __init__(self):
        super().__init__()
        BoardShim.enable_dev_board_logger()
        self.m = matlab.engine.start_matlab()
        # use synthetic board for demo
        params = BrainFlowInputParams()
        self.board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)
        print('starting EEG stream')
        self.board.prepare_session()
        self.board.start_stream()
        self.run=True
        self.data=[]
        self.temp_result=0
        self.savedata()
        

    def savedata (self):
        while self.run==True:
            self.data=[]
            time.sleep(1)
            self.data = self.board.get_board_data() # gets data from borad

            # feature extration
            bp_vals, rms_vals = self.m.bp_rms_extraction(self.data, nargout=2)
            bp_vals = list(bp_vals[0])
            rms_vals = list(rms_vals[0]) 

            # RMS classification
            rms_result =self.m.RMS_classification(rms_vals)
            rms_result = list(rms_result[0])
        
            # Bandpower classification
            bp_result =self.m.RMS_classification(bp_vals)
            bp_result = list(bp_result[0])

            # compere classification results
            if bp_result==rms_result:
                self.arm_out= rms_result
                self.temp_result=self.arm_out
            else :
                self.arm_out=self.temp_result 


            self.arm_control() # call arm control
        
            
    def arm_control (self):
        # function for controling robotic arm
        time.sleep(1)
        


    def closeEvent(self, event):
            # called by end timer
            self.run=False
            self.board.stop_stream()
            self.board.release_session()
            print('stop eeg stream ran')


if __name__ == "__main__":
   app = QApplication(sys.argv)
   main = win()
   main.show()
   sys.exit(app.exec())
