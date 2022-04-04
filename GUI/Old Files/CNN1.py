import os
from pyexpat import features
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import numpy as np
import sklearn
from sklearn.model_selection import train_test_split

dataset = []
# X = features
# y = labels 


(train_eeg, train_labels), (test_eeg, test_labels) =  train_test_split(X, y, test_size=0.33, random_state=42)

class_names = ['Movement', 'No Movement']

class_names1 = ['Left', 'None', 'Right']

print(train_eeg.shape)

# Baseline Normalizing: EEG Data time-frequenzy power
# Percent Change Baseline Normalization
# (100*(active period - baseline))/baseline


