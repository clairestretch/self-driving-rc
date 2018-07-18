from Inception_net import inception_v3 as googlenet
import numpy as np
import requests
import win32api
import time
import cv2
import os

car_speed = 600

esp_server = 'http://192.168.8.112'
camera_server = 'http://192.168.8.110:8080/video'

WIDTH = 320
HEIGHT = 240
LR = 0.01
MODEL_NAME = 'AI2.0'
model = googlenet(WIDTH, HEIGHT, 3, LR, output=8, model_name=MODEL_NAME)
model.load('model/{}'.format(MODEL_NAME))

def reset_car(payload):
    payload['drive'] = 0
    payload['turn'] = 0
    return payload

def send_command(payload, url=esp_server, response=False):
    try:
        r = requests.get(url, params=payload)
        if response:
            print(r.text, '\n')
    except Exception as e:
        print(e, '\n', 'Try again in 30 seconds.')
        time.sleep(30)

def main():
    car_on = False
    payload = dict()
    vid = cv2.VideoCapture(camera_server)
    payload['drivepwm'] = car_speed

    print('Countdown')
    for i in list(range(10))[::-1]:
        print(i+1)
        time.sleep(1)

    while True:
        ret, frame = vid.read()
        
        prediction = model.predict([frame.reshape(WIDTH,HEIGHT,3)])[0]
        #np.array([4.5, 0.1, 0.1, 0.1,  1.8, 1.8, 0.5, 0.5])
        prediction = np.array(prediction) * np.array([2, 2, 1, 1, .3, 1, 2, 2])
        mode_choice = np.argmax(prediction)
        
        payload = reset_car(payload)
        
        if mode_choice == 0:
            payload['drive'] = 1
            payload['turn'] = 1
            choice_picked = 'forward+left'
            
        elif mode_choice == 1:
            payload['drive'] = 1
            payload['turn'] = 2
            choice_picked = 'forward+right'
            
        elif mode_choice == 2:
            payload['drive'] = 2
            payload['turn'] = 1
            choice_picked = 'reverse+left'
            
        elif mode_choice == 3:
            payload['drive'] = 2
            payload['turn'] = 2
            choice_picked = 'reverse+right'
            
        elif mode_choice == 4:
            payload['drive'] = 1
            choice_picked = 'forward'
            
        elif mode_choice == 5:
            payload['drive'] = 2
            choice_picked = 'reverse'
            
        elif mode_choice == 6:
            payload['turn'] = 1
            choice_picked = 'left'
        elif mode_choice == 7:
            payload['turn'] = 2
            choice_picked = 'right'

        print(choice_picked)
        send_command(payload)
    
main()



















        
