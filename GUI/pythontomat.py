import matlab.engine
m = matlab.engine.start_matlab()

output = m.pythontest(7)
print(output)
