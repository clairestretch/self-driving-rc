import requests
from win32 import win32api
import time

url = 'http://192.168.8.112'
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
    while True:
        keysOn = keyState('WASD')
        if(keysOn):
            state = True
            payload['drive'] = 0
            payload['turn'] = 0
            payload['drivepwm'] = 0
            
            for key in keysOn:
                if(key == 'W'):
                    payload['drive'] = 1
                    payload['drivepwm'] = 1000
                if(key == 'S'):
                    payload['drive'] = 2
                    payload['drivepwm'] = 1000
                if(key == 'A'):
                    payload['turn'] = 1
                if(key == 'D'):
                    payload['turn'] = 2
            r = requests.get(url, params=payload)
            print(r.text, '\n')
        elif state:
            state = False
            payload['drive'] = 0
            payload['turn'] = 0
            payload['drivepwm'] = 0
            r = requests.get(url, params=payload)
            print(r.text, '\n')
main()
