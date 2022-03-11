import sys
import time
from turtle import shape

import numpy as np
import pandas as pd
import matplotlib as plt

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Dropout, Activation

from sklearn.model_selection import train_test_split

# Import eeg csv data

eeg1 = pd.read_csv(r'C:\Users\bcitteam\Documents\BCI-CAP\BCI-UBC\GUI\eeg2.csv')

print(eeg1)

def sliding_window_fft(chunk, win_size=50, step_size = 10, freq_low = 4, freq_high=38):
  '''
  Input:Chunk of eeg data (500 sample by 16 channel array (2 seconds of data))

  slides over chunk of eeg data with a 50 sample window size (shape (50,16)) (0.2 seconds)
  by steps of 7. 
  use this window to calculate the fft across time on all channels and select
  only frequencies between 4hz and 38hz
  add sliding window ffts to X and return X as training data

  output: list of 46 (7 frequency by 16 channel array)
  '''
  chunk_size = len(chunk)
  X = []

  #iterate over indices where i is the start of the window and i+win_size is the end
  for i in range(0, chunk_size - win_size + step_size, step_size):
    #get window

    win = chunk[i:i+win_size]
    #get fft of window for input data
    fft_data = np.absolute(np.fft.rfft(win,axis=0))
    fft_freqs = np.fft.rfftfreq(win.shape[0], 1.0 / 250) 

    relevant_inds = np.where((fft_freqs >= freq_low) & (fft_freqs <= freq_high))[0]
    relevant_data = fft_data[relevant_inds]

    X.append(relevant_data)
  return X

def get_valence_labeled_dataset(data, neg_thresh=3.5, pos_thresh=5.5):
  '''
  Input: pandas dataframe of labeled eeg data

  find each time t in the data where a stimulus is presented that has a valence
  score lower than neg_thresh or higher than pos_thresh (to ignore any middle valued valences
  since we're doing binary classification)

  The image was presented for 2.5 seconds (625 samples). Since it takes some 
  time for the brain to respond to the stimuli, we will take the eeg data from 
  time t+0.5 seconds to t+2.5 seconds (500 samples)

  Each chunk is processed by sliding_window_fft to turn a 500 sample by 16 channel 
  time domain array, to 46 shape (7,16) frequency domain arrays. These are all labeled
  with 1 or 0 depending on the valence score for the 500 sample chunk. 

  output: ~1000+ labeled training/testing samples

  '''
  tmin = 125
  tmax = 625
  X = []
  y = []

  #get indices where valence is less than or eq neg_thresh to label as negative (0)
  neg_inds = data[(data['Valence'] != 0.0) & (data['Valence'] <= neg_thresh)].index
  #get indices where valence is greater than or eq pos_thresh to label as positive (1)
  pos_inds = data[(data['Valence'] != 0.0) & (data['Valence'] >= pos_thresh)].index

  #get an even distribution of positive and negative labeled samples
  if len(neg_inds) < len(pos_inds):
    #get subset of pos_inds with equal size as neg_inds
    pos_inds = np.random.choice(pos_inds, len(neg_inds))
  
  elif len(pos_inds) < len(neg_inds):
    #get subset of neg_inds with equal size as pos_inds
    neg_inds = np.random.choice(neg_inds, len(pos_inds))

  for i in pos_inds:

    assert data.iloc[i]['Valence'] >= pos_thresh
    #get chunk of eeg from i+tmin to i+tmax, i is when the image was presented
    chunk = data.iloc[i+tmin:i+tmax].drop(['timestamps','Valence','Arousal'],axis=1).values
    #do a sliding window over the chunk and do an fft many more labeled samples
    fft_chunks = sliding_window_fft(chunk)
    labels = [np.array([1])] * len(fft_chunks)

    X.extend(fft_chunks)
    y.extend(labels)

  for i in neg_inds:

    assert data.iloc[i]['Valence'] <= neg_thresh
    #get chunk of eeg from i+tmin to i+tmax, i is when the image was presented
    chunk = data.iloc[i+tmin:i+tmax].drop(['timestamps','Valence','Arousal'],axis=1).values
    #do a sliding window over the chunk and do an fft many more labeled samples
    fft_chunks = sliding_window_fft(chunk)
    labels = [np.array([0])]*len(fft_chunks)

    X.extend(fft_chunks)
    y.extend(labels)

  return np.array(X), np.array(y)

x, y = get_valence_labeled_dataset(eeg1)

# convert y to one hot encoding
one_hot_y = np.zeros((y.size, 2))

# print(one_hot_y)
# print(one_hot_y.shape)

one_hot_y[np.arange(y.size), y.reshape(-1)] = 1
#print(one_hot_y)

eeg_x_train, eeg_x_test, eeg_y_train, eeg_y_test = train_test_split(x, one_hot_y, test_size=.2)

# print(eeg_x_train)
# print(eeg_y_train)

dropout_rate = .1
eeg_model = Sequential([
])

eeg_model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
eeg_history = eeg_model.fit(eeg_x_train, eeg_y_train, batch_size=32, epochs=1)

plt.plot(eeg_history.epoch, eeg_history.history['loss'])
plt.axhline(eeg_model.evaluate(eeg_x_test, eeg_y_test)[0], color='r')

plt.plot(eeg_history.epoch, eeg_history.history['accuracy'])
plt.axhline(eeg_model.evaluate(eeg_x_test, eeg_y_test)[1], color='r')
plt.ylim(0, 1)