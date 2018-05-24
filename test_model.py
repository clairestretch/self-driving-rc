from control import car
import numpy as np
import cv2
import time
from alexnet import alexnet
import random
from win32 import win32api

WIDTH = 80
HEIGHT = 60
LR = 1e-3
EPOCHS = 10
MODEL_NAME = 'alexnet_model/rc-{}-{}-{}-epochs.model'.format(LR, 'alexnetv2',EPOCHS)
 
model = alexnet(WIDTH, HEIGHT, LR)
model.load(MODEL_NAME)

def main():
    last_time = time.time()
    for i in list(range(4))[::-1]:
        print(i+1)
        time.sleep(1)

    paused = False
    #IP camera video stream URL
    cam_url = 'http://192.168.8.100:8080/video'
    cam = cv2.VideoCapture(cam_url)
    #ESP 8266 server URL
    test_rig = car('http://192.168.8.108/controls')
    
    while(True):
        if not paused:
            ret, screen = cam.read()
            last_time = time.time()
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            screen = cv2.resize(screen, (80,60))

            prediction = model.predict([screen.reshape(80,60,1)])[0]
            print(prediction)

            turn_thresh = .75
            fwd_thresh = 0.70

            if prediction[0] > turn_thresh:
                test_rig.left()
                test_rig.forward()
            elif prediction[2] > turn_thresh:
                test_rig.right()
                test_rig.forward()
            elif prediction[1] > fwd_thresh:
                test_rig.forward()
            else:
                test_rig.stop()

        state = win32api.GetAsyncKeyState(ord('T'))
        if(state < 0 or state == 1):
            if paused:
                cam = cv2.VideoCapture(cam_url)
                paused = False
                time.sleep(1)
            else:
                paused = True
                time.sleep(1)

main()       
