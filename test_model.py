from control import car
import numpy as np
import cv2
import time
from alexnet import alexnet
import random
from win32 import win32api

WIDTH = 160
HEIGHT = 120
LR = 1e-3
EPOCHS = 15
MODEL_NAME = 'alexnet_model/rc-{}-{}-{}-epochs.model'.format(LR, 'alexnetv2',EPOCHS)
 
model = alexnet(WIDTH, HEIGHT, LR)
model.load(MODEL_NAME)

def main():
    last_time = time.time()
    for i in list(range(4))[::-1]:
        print(i+1)
        time.sleep(1)

    paused = False
    cam_url = 'http://192.168.8.110:8080/video'
    cam = cv2.VideoCapture(cam_url)
    test_rig = car('http://192.168.8.108/controls')
    
    while(True):
        
        if not paused:
            cam = cv2.VideoCapture(cam_url)
            ret, screen = cam.read()
            last_time = time.time()
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            screen = cv2.resize(screen, (WIDTH, HEIGHT))

            prediction = model.predict([screen.reshape(WIDTH, HEIGHT,1)])[0]
            print(prediction)

            turn_thresh = 0.75
            fwd_thresh = 0.50

            if prediction[1] > turn_thresh and max(prediction) == prediction[1]:
                print('LEFT\n')
                test_rig.left()
                test_rig.forward()
            elif prediction[2] > turn_thresh and max(prediction) == prediction[2]:
                print('RIGHT\n')
                test_rig.right()
                test_rig.forward()
            elif prediction[0] > fwd_thresh:
                print('FORWARD\n')
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
