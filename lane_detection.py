import numpy as np
import cv2
import time
from numpy import ones,vstack
from numpy.linalg import lstsq
from statistics import mean

class lane_gen:
    def __init__(self):
        self.vertices = np.array([[0, 500], [0, 300],
                                [300, 200], [500, 200],
                                [800, 300], [800, 500]])

    def image_resize(self, image, width=None, height=None, inter = cv2.INTER_AREA):
        dim = None
        (h, w) = image.shape[:2]
        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))
        resized = cv2.resize(image, dim, interpolation = inter)
        return resized
    
    def draw_lanes(self, lines, color=[0, 255, 255], thickness=3):

        # if this fails, go with some default line
        try:

            # finds the maximum y value for a lane marker 
            # (since we cannot assume the horizon will always be at the same point.)

            ys = []  
            for i in lines:
                for ii in i:
                    ys += [ii[1],ii[3]]
            min_y = min(ys)
            max_y = 600
            new_lines = []
            line_dict = {}

            for idx,i in enumerate(lines):
                for xyxy in i:
                    # These four lines:
                    # modified from http://stackoverflow.com/questions/21565994/method-to-return-the-equation-of-a-straight-line-given-two-points
                    # Used to calculate the definition of a line, given two sets of coords.
                    x_coords = (xyxy[0],xyxy[2])
                    y_coords = (xyxy[1],xyxy[3])
                    A = vstack([x_coords, ones(len(x_coords))]).T
                    m, b = lstsq(A, y_coords, rcond=None)[0]

                    # Calculating our new, and improved, xs
                    x1 = (min_y-b) / m
                    x2 = (max_y-b) / m

                    line_dict[idx] = [m,b,[int(x1), min_y, int(x2), max_y]]
                    new_lines.append([int(x1), min_y, int(x2), max_y])

            final_lanes = {}

            for idx in line_dict:
                final_lanes_copy = final_lanes.copy()
                m = line_dict[idx][0]
                b = line_dict[idx][1]
                line = line_dict[idx][2]
                
                if len(final_lanes) == 0:
                    final_lanes[m] = [ [m,b,line] ]
                    
                else:
                    found_copy = False

                    for other_ms in final_lanes_copy:

                        if not found_copy:
                            if abs(other_ms*1.2) > abs(m) > abs(other_ms*0.8):
                                if abs(final_lanes_copy[other_ms][0][1]*1.2) > abs(b) > abs(final_lanes_copy[other_ms][0][1]*0.8):
                                    final_lanes[other_ms].append([m,b,line])
                                    found_copy = True
                                    break
                            else:
                                final_lanes[m] = [ [m,b,line] ]

            line_counter = {}

            for lanes in final_lanes:
                line_counter[lanes] = len(final_lanes[lanes])

            top_lanes = sorted(line_counter.items(), key=lambda item: item[1])[::-1][:2]

            lane1_id = top_lanes[0][0]
            lane2_id = top_lanes[1][0]

            def average_lane(lane_data):
                x1s = []
                y1s = []
                x2s = []
                y2s = []
                for data in lane_data:
                    x1s.append(data[2][0])
                    y1s.append(data[2][1])
                    x2s.append(data[2][2])
                    y2s.append(data[2][3])
                return int(mean(x1s)), int(mean(y1s)), int(mean(x2s)), int(mean(y2s)) 

            l1_x1, l1_y1, l1_x2, l1_y2 = average_lane(final_lanes[lane1_id])
            l2_x1, l2_y1, l2_x2, l2_y2 = average_lane(final_lanes[lane2_id])

            return [l1_x1, l1_y1, l1_x2, l1_y2], [l2_x1, l2_y1, l2_x2, l2_y2], lane1_id, lane2_id
        except Exception as e:
            print(str(e))
        
    def generate_path(self):
        self.terrain = cv2.Canny(self.terrain, threshold1=200, threshold2=300)
        self.terrain = self.region_of_intrest(self.terrain, self.vertices)

        self.terrain = cv2.GaussianBlur(self.terrain, (5,5), 0)
        #hough Line detection.                                  , maxLineLength, maxLineGap)
        lines = cv2.HoughLinesP(self.terrain, 1, np.pi/180, 180, np.array([]), 20, 15)
        
        m1 = 0
        m2 = 0
        try:
            l1, l2, m1,m2 = self.draw_lanes(lines)
            cv2.line(self.orginal, (l1[0], l1[1]), (l1[2], l1[3]), [0,255,0], 30)
            cv2.line(self.orginal, (l2[0], l2[1]), (l2[2], l2[3]), [0,255,0], 30)
        except Exception as e:
            print(str(e))
            pass
        try:
            for coords in lines:
                coords = coords[0]
                try:
                    cv2.line(self.terrain, (coords[0], coords[1]), (coords[2], coords[3]), [255,0,0], 3)
                    
                except Exception as e:
                    print(str(e))
        except Exception as e:
            pass
        cv2.imshow('image', self.orginal)

    def video_cap(self, url):
        cam = cv2.VideoCapture(url)
        while True:
            ret,self.terrain = cam.read()
            self.orginal = self.terrain
            self.generate_path()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cam.release()
        cv2.destroyAllWindows()

    def region_of_intrest(self, img, vertices):
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, [vertices], 255)
        masked = cv2.bitwise_and(img, mask)
        return masked
        
    def image_test(self, path):
        self.orginal = self.terrain = cv2.imread(path)
        self.orginal = self.terrain = self.image_resize(self.terrain, width=800, height=600)
        self.generate_path()
        
    

debug = lane_gen()
#debug.image_test('2.jpg')

debug.video_cap('http://192.168.8.101:8080/video')
