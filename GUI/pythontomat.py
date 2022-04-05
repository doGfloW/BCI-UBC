import matlab.engine

m = matlab.engine.start_matlab()
# data_txtfile = r"mateo_2sec_for_testing.txt"
data_txtfile = r"alexis_nonlive_testing.txt"

bp_class, rms_class, bp_vals, rms_vals = m.bp_rms_extraction(data_txtfile, 0, nargout=4)
# rms_class = list(rms_class[0])
print('bp_class', bp_class)
print('rms_class', rms_class)
# bp_vals = list(bp_vals[0])
# rms_vals = list(rms_vals[0])
print('bp', bp_vals)
print('rms', rms_vals)

# import argparse
# import time
# import numpy as np
# import pandas as pd
# import sys
#
# import brainflow
# from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
#
# import matlab.engine
#
# m = matlab.engine.start_matlab()
#
# BoardShim.enable_dev_board_logger()
# m = matlab.engine.start_matlab()
# # use synthetic board for demo
# params = BrainFlowInputParams()
# board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)
# board.prepare_session()
# board.start_stream()
# time.sleep(1)
# data = board.get_board_data() # gets data from borad
# board.stop_stream()
# board.release_session()
# data = data.tolist()
# data = m.readtable(data)
# print(data)
# print(type(data))
# # feature extration
# bp_vals, rms_vals = m.bp_rms_extraction(data, nargout=2)
# bp_vals = list(bp_vals[0])
# rms_vals = list(rms_vals[0])
