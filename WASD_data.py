import numpy as np
import cv2
import requests
import win32api
import time
import os


url = 'http://192.168.8.108/controls'
cam_url = 'http://192.168.8.110:8080/video'

file_name = 'training_data.npy'

if os.path.isfile(file_name):
    print('File exists, loading previous data.')
    training_data = list(np.load(file_name))
else:
    print('file does not exist, new data started.')
    training_data = []

def keyState(keys):
    stack = []
    for key in keys:
        state = win32api.GetAsyncKeyState(ord(key))
        if(state < 0 or state == 1):
            stack.append(key)
    return stack

def main():
    state = False
    payload = {}
    prevKeys = ()
    cam = cv2.VideoCapture(cam_url)
    
    while True:
        ret, frame = cam.read()
        output = [0, 0, 0]
        keysOn = keyState('WASD')
        
        if(keysOn):
            #save what type of movement for accepted moves for each frame.
            if 'W' in keysOn:
                output = [1, 0, 0]
                if 'A' in keysOn:
                    output = [0, 1, 0]
                elif 'D' in keysOn:
                    output = [0, 0, 1]
                    
            state = True
            # set values to defualt if they are not changed.
            payload['Relay'] = 2
            payload['steerAngle'] = 68
            
            for key in keysOn:
                if(key == 'W'):
                    payload['Relay'] = 0
                    
                if(key == 'S'):
                    payload['Relay'] = 1
                    
                if(key == 'A'):
                    payload['steerAngle'] = 45
                    
                if(key == 'D'):
                    payload['steerAngle'] = 95
                    
            r = requests.get(url, params=payload)
            print(r.text, '\n')
            
            #store frame and one hot array
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.resize(frame,(160,120))
            training_data.append([frame, output])
            
            #save data when it reaches 500 frames.
            if len(training_data) % 500 == 0:
                print(len(training_data))
                np.save(file_name, training_data)
              
        elif state:
            state = False
            payload['Relay'] = 2
            payload['steerAngle'] = 68
            r = requests.get(url, params=payload)
            print(r.text, '\n')
main()
