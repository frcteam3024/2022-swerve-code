import math
import cv2
import numpy as np
from networktables import NetworkTables
import datetime as dt

Display = 1
Use_camera = 1
Read_file = 0
Home_target = 1

ILH = 66 #Low hue
IHH = 113 #High hue
ILS = 167 #Low saturation
IHS = 255 #High saturation
ILV = 135 #Low value
IHV = 255 #High value

Target_width = 48
Target_height = 83
Camera_height = 46

Camera_pixel_h = 480
Camera_pixel_w = 640
Robot_center_xd = 321
Robot_horizon_y = 17

#Global variables
#didn't do this yet, old/new distance
rho = 2
thr = 4
#left out dwidht and dheight
oldSecs = 0
numFrames = 0
#left out "point pt1A, pt2A" cv2.KeyPoint (?)
#left out"int can1, can2, can3"
iDelTheta = 3
oldTime = 0
oldSecs = 0

#left out Mat fileMat and Mat cameraMat

camera_window = "3rd: Camera Window"
thresh_window = "3rd: Thresh Window"
edges_window = "3rd: Edges Window"

#left out "unsigned long long" and "struct"

def reportFrames(oldTime, oldSecs):
    newTime = 1000000 * int(dt.datetime.now().second) + int(dt.datetime.now().microsecond)
    elapsed = newTime - oldTime
    oldTime = newTime
    newSecs = newTime / 1000000
    if newSecs < oldSecs + 10: #report every 10 seconds
        numFrames += 1
        if oldSecs == 0:
            oldSecs = newSecs
        else:
            print('%d new frames \n', numFrames) #ignored if 1:
            numFrames = 1
            oldSecs = newSecs

cap = cv2.VideoCapture(0)

def main(argc, argv): #if it's not working, this is why

    cv2.namedWindow('Camera', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('Edges', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('thresh', cv2.WINDOW_AUTOSIZE)

    #missing #if Read_file
    #print("read movie \n")
    cap = cv2.VideoCapture(0)
    #cap.open("IMG_1179.mp4")

    #missing #if Use_camera

    print("use camera \n")
    #left out videoCapture

    def do_the_thing():
        if not cap.isOpened():
            print("error opening video stream or file")
            return (-1)
    do_the_thing()

img = cap.read() #Using this instead of cap >> cameraMat, might not work
cap.grab()

if fileMat.empty():
    print("frame empty \n")
else:
    print("got initial frame \n")
    
    
reportFrames(oldTime, oldSecs)























