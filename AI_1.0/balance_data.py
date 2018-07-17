import cv2
import numpy as np
import time
import pandas as pd
from collections import Counter
from random import shuffle

file = np.load('training_data.npy')

newfile = []
straight = []
for data in file:
    if data[1] == [1, 0, 0]:
        straight.append(data)
    elif data[1] != [0, 0, 0]:
        newfile.append(data)
        

newfile += straight[:int(len(newfile)/2)]

shuffle(newfile)

np.save('training_data_balanced.npy', newfile)



##for data in file:
##    cv2.imshow('video', data[0])
##    if cv2.waitKey(1) & 0xFF == ord('q'):
##        break
##    print(data[1])
##    time.sleep(.01)
##    
