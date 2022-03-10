#test new models

#from liblsl import StreamInlet, resolve_stream
from pydoc import resolve
import numpy as np
import time
import matplotlib
import sys
from collections import deque

print("looking for streams...")
streams = resolve