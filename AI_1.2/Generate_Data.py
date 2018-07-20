from random import shuffle
import numpy as np
import requests
import win32api
import time
import cv2
import os

image_size = (320, 240)
#pwm 0 - 1023
car_speed = 900

action = {
    'AW': [1, 0, 0, 0, 0, 0, 0, 0],
    'DW': [0, 1, 0, 0, 0, 0, 0, 0],
    'AS': [0, 0, 1, 0, 0, 0, 0, 0],
    'DS': [0, 0, 0, 1, 0, 0, 0, 0],
    'W' : [0, 0, 0, 0, 1, 0, 0, 0],
    'S' : [0, 0, 0, 0, 0, 1, 0, 0],
    'A' : [0, 0, 0, 0, 0, 0, 1, 0],
    'D' : [0, 0, 0, 0, 0, 0, 0, 1],
    }

esp_server = 'http://192.168.8.112'
camera_server = 'http://192.168.8.110:8080/video'

def keyState(keys='WASD'):
    keys_on = []
    for key in keys:
        state = win32api.GetAsyncKeyState(ord(key))
        if(state < 0 or state == 1):
            keys_on.append(key)
    return keys_on

def save_file(imgs, num):
    #imgs = list(filter(lambda a: a[1] != NA, imgs))
    shuffle(imgs)
    np.save('data/training_data-{}.npy'.format(num), imgs)

def reset_car(payload):
    payload['drive'] = 0
    payload['turn'] = 0
    payload['drivepwm'] = 0
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
    training_data = list()
    vid = cv2.VideoCapture(camera_server)
    file_num = 1
    
    while True:
        file_name = 'data/training_data-{}.npy'.format(file_num)

        if os.path.isfile(file_name):
            print('File exists, moving along', file_num)
            file_num += 1
        else:
            print('Starting at {}.'.format(file_num))
            break
    
    while True:
        ret, frame = vid.read()
        keys_on = keyState()
        if keys_on:
            keys_on.sort()
            keys_on = ''.join(keys_on)
            if keys_on in action:
                print(keys_on)
                output = action[keys_on]
                payload = reset_car(payload)
                for key in keys_on:
                    if(key == 'W'):
                        payload['drive'] = 1
                        payload['drivepwm'] = car_speed
                    if(key == 'S'):
                        payload['drive'] = 2
                        payload['drivepwm'] = car_speed
                    if(key == 'A'):
                        payload['turn'] = 1
                    if(key == 'D'):
                        payload['turn'] = 2
                send_command(payload)
                car_on = True
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #frame = cv2.resize(frame, image_size)
                training_data.append([frame, output])
                if len(training_data) % 2000 == 0:
                    print('starting save')
                    payload = reset_car(payload)
                    send_command(payload)
                    save_file(training_data, file_num)
                    file_num += 1
                    training_data = list()
                    print('saved')
                    
        elif car_on:
            car_on = False
            payload = reset_car(payload)
            send_command(payload)
main()
