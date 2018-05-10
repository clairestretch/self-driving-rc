import requests

#KEY:

#(Forward, Relay = 1), (Backward, Relay = 0), (No Acceleration, Stop = 1),
#(Left, steerAngle = 60), (Right, steerAngle = 100), (Straight, steerAngle = 80) ~ 70)

class car:
    def __init__(self, espURL, debug=False):
        self.debug = debug
        self.url = espURL
        self.payload = {'Relay': None,
                        'steerAngle': None,
                        'Stop': None
                        }
    def forward(self):
        self.payload['Relay'] = 1
        r = requests.get(self.url, params=self.payload)
        if self.debug:
            print(r.text, '\n')  
    def backward(self):
        self.payload['Relay'] = 0
        r = requests.get(self.url, params=self.payload)
        if self.debug:
            print(r.text, '\n')  
    def stop(self):
        self.payload['Relay'] = 2
        r = requests.get(self.url, params=self.payload)
        if self.debug:
            print(r.text, '\n')  
    def left(self):
        self.payload['steerAngle'] = 60
        r = requests.get(self.url, params=self.payload)
        if self.debug:
            print(r.text, '\n') 
    def right(self):
        self.payload['steerAngle'] = 100
        r = requests.get(self.url, params=self.payload)
        if self.debug:
            print(r.text, '\n') 
    def straight(self):
        self.payload['steerAngle'] = 70
        r = requests.get(self.url, params=self.payload)
        if self.debug:
            print(r.text, '\n') 
    
