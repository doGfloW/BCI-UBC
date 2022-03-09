import matlab.engine
m = matlab.engine.start_matlab()
x = m.sqrt(42.0)
print(x)