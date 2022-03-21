import matlab.engine
m = matlab.engine.start_matlab()
data_txtfile = r"C:\Users\alyna\Documents\ENGR 499\BCI-UBC\Matlab\mateo_2sec_for_testing.txt"
output = m.bandpower_extraction(data_txtfile)
output = list(output[0])
print(output)
