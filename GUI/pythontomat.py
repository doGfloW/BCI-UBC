import matlab.engine
m = matlab.engine.start_matlab()
data_txtfile = r"mateo_2sec_for_testing.txt"
output = m.bandpower_extraction(data_txtfile)
output = list(output[0])
print(output)
