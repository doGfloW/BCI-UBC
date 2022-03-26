import matlab.engine
import pandas as pd
import sys

m = matlab.engine.start_matlab()
data_txtfile = r"mateo_2sec_for_testing.txt"

bp_vals, rms_vals = m.bp_rms_extraction(data_txtfile, nargout=2)
bp_vals = list(bp_vals[0])
rms_vals = list(rms_vals[0])
print('bp', bp_vals)
print('rms', rms_vals)
