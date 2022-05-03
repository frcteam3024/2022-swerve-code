#imports
import cv2
import math
import numpy as np
import datetime as dt
from networktables import NetworkTables    #MIGHT BE NETWORKTABLE

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

def line_intersection(line1, line2):  # this is used in calc_image to help find line intersections
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] *b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return None

    d = (det(*line1), det(*line2))                                                                                             
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    
    return int(x), int(y)

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





    
    intersect_array = []
    theta_array = []

    leftmostXleft = 1000
    lowestYleft = -1000
    oldDistLeft = 1000
    rightmostXright = -1000
    lowestYright = -1000
    oldDistRight = 1000

    
    if line_data is None:
        ithreshold -= 1
        cv2.setTrackbarPos('threshold', 'Camera', ithreshold)
    else:
        i = 0
        line_data_len = len(line_data)
        lineLimitHigh = ihigh_lines_num
        lineLimitLow = ilow_lines_num
        if (line_data_len > lineLimitHigh):
            line_data_len = lineLimitHigh
            ithreshold += 1
            cv2.setTrackbarPos('threshold', 'Camera', ithreshold)
        elif (line_data_len < lineLimitLow):
            ithreshold -= 1
            print('updating threshold to ', ithreshold)
            cv2.setTrackbarPos('threshold', 'Camera', ithreshold)

        numPlus60 = 0
        numMinus60 = 0
        numZero = 0

        leftmostXleft = 1000
        lowestYleft = -1000
        oldDistLeft = 1000
        rightmostXright = -1000
        lowestYright = -1000
        oldDistRight = 1000

        print('left: {}, right: {}, bottom left: {}, bottom right: {}'.format(oldDistLeft,oldDistRight,lowestYleft,lowestYright))

    if line_data is None:  # to avoid nonetype errors
        ERROR = 1
        pass

    cv2.imshow('Edges', edges)
    #cv2.waitKey(1)
    
    return intersect_array, theta_array, frame


    '''

    numPlus60 = 0
    numMinus60 = 0
    numZero = 0
    
    if line_data is None:
        ithreshold -= 1
        cv2.setTrackbarPos('threshold', 'Camera', ithreshold)
    else:
        i = 0
        line_data_len = len(line_data)
        lineLimitHigh = ihigh_lines_num
        lineLimitLow = ilow_lines_num
        if (line_data_len > lineLimitHigh):
            line_data_len = lineLimitHigh
            ithreshold += 1
            cv2.setTrackbarPos('threshold', 'Camera', ithreshold)
        elif (line_data_len < lineLimitLow):
            ithreshold -= 1
            print('reducing threshold to ', ithreshold)
            cv2.setTrackbarPos('threshold', 'Camera', ithreshold)

        while i < line_data_len:
            for rho, theta in line_data[i]:
                commonTheta = theta * 57.2958 - 90;
                got_horiz = 0
                if (commonTheta < -45):
                    numMinus60 += 1
                elif (commonTheta < 45):
                    numZero += 1
                    got_horiz = 1
                elif (commonTheta > 45):
                    numPlus60 += 1
                else:
                    print('Illegal commonTheta ', commonTheta)
                aA = np.cos(theta)
                bA = np.sin(theta)
                x0A = aA*rho
                y0A = bA*rho
                x1 = int(x0A + 1000 * (-bA))
                y1 = int(y0A + 1000 * (aA))
                x2 = int(x0A - 1000 * (-bA))
                y2 = int(y0A - 1000 * (aA))

                cv2.line(frame, (x1,y1), (x2,y2), (63, 63, 63), 1, 1)
                j = 0
                while j < line_data_len:
                    if i == j:
                        j += 1
                    else:
                        for rhob, thetab in line_data[j]:
                            aB = np.cos(thetab)
                            bB = np.sin(thetab)
                            x0B = aB*rhob
                            y0B = bB*rhob
                            x3 = int(x0B + 1000 * (-bB))
                            y3 = int(y0B + 1000 * (aB))
                            x4 = int(x0B - 1000 * (-bB))
                            y4 = int(y0B - 1000 * (aB))
                            line1 = ((x1, y1), (x2, y2))
                            line2 = ((x3, y3), (x4, y4))
                            intersect = line_intersection(line1, line2)
                            if intersect == None:
                                x=1
                            else:
                                tha = theta * 57.2958 - 90
                                thb = thetab * 57.2958 - 90
                                if abs(tha - thb) > 10:  # ignore parallel lines
                                    intersect_array.append(intersect)
                                    theta_array.append((theta, thetab))
                                    for x, y in [intersect]:
                                        if tha > -45 and tha < 45 and thb > 45:  # a is horizontal and b is 60
                                            distLeft = int(math.sqrt( x ** 2 + (480 - y) ** 2))
                                            if distLeft < oldDistLeft:
                                                oldDistLeft = distLeft
                                                hLx = x
                                                hLy = y
                                        if tha > -45 and tha < 45 and thb < -45:  # a is horizontal and b is -60
                                            distRight = int(math.sqrt( (640 - x) ** 2 + (480 - y) ** 2))
                                            if distRight < oldDistRight:
                                                oldDistRight = distRight
                                                hRx = x
                                                hRy = y
                                    
                            j += 1
                i += 1
    


        '''
        #IMPORTANT: avoids nonetype error
    if line_data is None:
        return   
        ''' 
    
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
    '''
    
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





