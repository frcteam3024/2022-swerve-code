#imports
import cv2
import math
import numpy as np
import datetime as dt
from networktables import NetworkTables

# set up network tables
NetworkTables.initialize(server='10.30.24.2')
print('NT connected: ', NetworkTables.isConnected())
netTable = NetworkTables.getTable('Pi')

#probably not being used
"""camera_window = "3rd: Camera Window"
edges_window = "3rd: Edges Window"""

#callback for the trackbars
def nothing(x):
    pass

def image(cap):
    ret, frame = cap.read()
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)
    
    ilowH = cv2.getTrackbarPos('lowH', 'Camera')
    ilowS = cv2.getTrackbarPos('lowS', 'Camera')
    ilowV = cv2.getTrackbarPos('lowV', 'Camera')
    ihighH = cv2.getTrackbarPos('highH', 'Camera')
    ihighS = cv2.getTrackbarPos('highS', 'Camera')
    ihighV = cv2.getTrackbarPos('highV', 'Camera')
    ithreshold = cv2.getTrackbarPos('threshold', 'Camera')
    ihigh_lines_num = cv2.getTrackbarPos('linesNumHigh', 'Edges')
    ilow_lines_num = cv2.getTrackbarPos('linesNumLow', 'Edges')

    #convert to HSV
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #more trackbar stuff
    low_hsv = np.array([ilowH, ilowS, ilowV])
    high_hsv = np.array([ihighH, ihighS, ihighV])
    mask = cv2.inRange(grey, low_hsv, high_hsv)
    frame = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow('newCamera', frame)
    cv2.waitKey(1)

    edges = cv2.Canny(mask, 50, 150, apertureSize=3)
    #cv2.imshow('Edges', edges)

    cv2.waitKey(1)
    min_length = 50
    max_gap = 10
    line_data = cv2.HoughLines(edges, 1, math.pi/180, ithreshold)

    #IMPORTANT: avoids nonetype error
    if line_data is None:
         return   

    botm = 1000 # start at top and move down
    left = 1000 # start at right and move left
    rigt = -1000 # start left and move right
    usedLines = 0
    lineMax = 50
        
    for line in line_data:
        #time_0 = 1000000 * int(dt.datetime.now().second) + int(dt.datetime.now().microsecond)
        
        rho, theta = line[0]
        rhoDeg = 180/math.pi*rho
        thetaDeg = 180/math.pi*theta
        #print("rho: {}, theta: {}".format(rho, theta))
        aA = math.cos(theta)
        bA = math.sin(theta)
        x0A = aA * rho
        y0A = bA * rho
        x1 = int(x0A - 1000 * bA)
        y1 = int(y0A + 1000 * aA)
        x2 = int(x0A + 1000 * bA)
        y2 = int(y0A - 1000 * aA)

        pt1 = (x1, y1)
        pt2 = (x2, y2)

        #print(pt1, pt2)

        
        # if lines are within 2 degrees of horizontal or vertical
        if abs(abs(thetaDeg-45)-45) <= 2 and usedLines <= lineMax:
            #draw lines
            # lines should be green?
            cv2.line(edges, pt1, pt2, (255, 0, 0), 1, 1)

            # if line is vertical
            if abs(thetaDeg) <= 2:
                avgX = (x1+x2)/2
                if avgX < left:
                    left = avgX
                if avgX > rigt:
                    rigt = avgX

            # if line is horizontal
            if abs(thetaDeg-90) <= 2:
                avgY = (y1+y2)/2
                if avgY < botm:
                    botm = avgY
            usedLines += 1

        # ask Eryl why we get 2700 fps
        #time_f = 1000000 * int(dt.datetime.now().second) + int(dt.datetime.now().microsecond)
        #time_diff = (time_f - time_0) / 1000000
        #fps = time_diff ** -1
        #print(fps)
        
    cv2.imshow('Edges', edges)
    #cv2.waitKey(1)

    #print('left: {}, right: {}, bottom: {}'.format(left,rigt,botm))
    
    cv2.waitKey(1)

    #print('left: {}, right: {}, bottom: {}'.format(left,rigt,botm))
    
    return frame

def main():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    cv2.namedWindow('Camera', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('Edges', cv2.WINDOW_AUTOSIZE)
    cv2.waitKey(1)
    
    ILH = 73   #low hue
    IHH = 100  #high hue
    ILS = 167  #low saturation
    IHS = 255  #high saturation
    ILV = 115  #low value / intensity
    IHV = 145  #high value / intensity
    THRESH = 3 #threshold for lines (length of eges that count as lines)

    #set up trackbars
    cv2.createTrackbar('lowH', 'Camera', ILH, 255, nothing)
    cv2.createTrackbar('highH', 'Camera', IHH, 255, nothing)
    cv2.createTrackbar('lowS', 'Camera', ILS, 255, nothing)
    cv2.createTrackbar('highS','Camera', IHS, 255, nothing)
    cv2.createTrackbar('lowV', 'Camera', ILV, 255, nothing)
    cv2.createTrackbar('highV', 'Camera', IHV, 255, nothing)
    cv2.createTrackbar('threshold', 'Camera', THRESH, 120, nothing)
    #possibly not being used
    cv2.createTrackbar('linesNumLow','Edges', 17, 30, nothing)
    cv2.createTrackbar('linesNumHigh','Edges', 19, 30, nothing)

    cv2.waitKey(1)

    cv2.imshow('Camera', frame)
    cv2.waitKey(1)
    
    while True:
        image(cap)
        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()





