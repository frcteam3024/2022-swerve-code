#imports
import cv2
import math
import numpy as np
import datetime as dt
from networktables import NetworkTables
import threading

show_debug = True
enable_networking = False

camera_width = 320
camera_height = 240
camera_fov = 20

# For networking
cond = threading.Condition()
notified = [False]

def connection_listener(connected, info):
    print(info, '; Connected=%s' % connected)
    with cond:
        notified[0] = True
        cond.notify()

# Callback for the trackbars

def nothing(x):
    pass

def get_binary_image(frame):
    lowH = cv2.getTrackbarPos('lowH', 'Camera')
    lowS = cv2.getTrackbarPos('lowS', 'Camera')
    lowV = cv2.getTrackbarPos('lowV', 'Camera')
    highH = cv2.getTrackbarPos('highH', 'Camera')
    highS = cv2.getTrackbarPos('highS', 'Camera')
    highV = cv2.getTrackbarPos('highV', 'Camera')

    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Mask based on trackbar settings
    low_hsv = np.array([lowH, lowS, lowV])
    high_hsv = np.array([highH, highS, highV])
    mask = cv2.inRange(hsv, low_hsv, high_hsv)
    masked_frame = cv2.bitwise_and(hsv, hsv, mask=mask)
    
    # Convert to grayscale and threshold it to make it a binary image
    grey_image = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)
    _, thresholded_frame = cv2.threshold(grey_image, 10, 255, cv2.THRESH_BINARY)
    if show_debug:
        cv2.imshow('After thresholding', thresholded_frame)

    return thresholded_frame

def analyze_image(cap):
    ret, frame = cap.read()
    frame = cv2.resize(frame, (camera_width, camera_height))
    if show_debug:
        cv2.imshow('Camera', frame)
        cv2.waitKey(1)

    binary_frame = get_binary_image(frame)

    frame_contours, contours, heirarchy = cv2.findContours(binary_frame, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    areaThreshold = cv2.getTrackbarPos('Area Threshold', 'Camera')
    aspectRatioMin = cv2.getTrackbarPos('Aspect Ratio Min (%)', 'Camera') / 100.0
    aspectRatioMax = cv2.getTrackbarPos('Aspect Ratio Max (%)', 'Camera') / 100.0
    solidityThreshold = cv2.getTrackbarPos('Solidity Threshold (%)', 'Camera') / 100.0
    polygonApproxAccuracy = cv2.getTrackbarPos('Polygon Approx Accuracy (%)', 'Camera') / 100.0

    locationX = 0
    locationY = 0
    validContours = []
    numValidContours = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < areaThreshold:
            continue
        
        # This could be used for the aspect ratio calculation if the edges
        # of the targets are not horizontal enough for the normal bounding box
        '''
        rotatedRect = cv2.minAreaRect(contour)
        aspectRatio = float(rotatedRect[1][0]) / rotatedRect[1][1]
        if aspectRatio < 1:
            aspectRatio = 1.0 / aspectRatio
        '''
        
        x, y, w, h = cv2.boundingRect(contour)
        aspectRatio = float(w) / h
        
        if aspectRatio < aspectRatioMin or aspectRatio > aspectRatioMax:
            continue
        
        hull = cv2.convexHull(contour)
        hullArea = cv2.contourArea(hull)
        solidity = float(area) / hullArea
        if solidity < solidityThreshold:
            continue

        epsilon = polygonApproxAccuracy * cv2.arcLength(contour, True)
        polygon = cv2.approxPolyDP(contour, epsilon, True)
        if len(polygon) > 5:
            continue

        moments = cv2.moments(contour)
        locationX += moments['m10'] / moments['m00']
        locationY += moments['m01'] / moments['m00']
        if show_debug:
            validContours.append(contour)
        numValidContours += 1

    if show_debug:
        #print("Contours: {}, Valid contours: {}".format(len(contours), numValidContours))
        cv2.drawContours(frame, validContours, -1, (31, 95, 255), 1)
        cv2.imshow("Contours", frame)
        cv2.waitKey(1)

    if numValidContours == 0:
        return -1, -1

    locationX /= numValidContours
    locationY /= numValidContours

    return locationX, locationY

def connect_to_roborio():
    NetworkTables.initialize(server='10.30.24.2')
    NetworkTables.addConnectionListener(connection_listener, immediateNotify=True)
    with cond:
        print('Waiting to connect to roborio...')
        if not notified[0]:
            cond.wait()
    print('Connected')
    netTable = NetworkTables.getTable('Pi')
    return netTable

def init_trackbars():
    # Defaults
    low_hue = 60
    high_hue = 100
    low_saturation = 120
    high_saturation = 255
    low_value = 100
    high_value = 255

    areaThreshold = 20
    aspectRatioMin = 150
    aspectRatioMax = 400
    solidityThreshold = 80
    polygonApproxAccuracy = 5

    # Create trackbars
    cv2.createTrackbar('lowH', 'Camera', low_hue, 255, nothing)
    cv2.createTrackbar('highH', 'Camera', high_hue, 255, nothing)
    cv2.createTrackbar('lowS', 'Camera', low_saturation, 255, nothing)
    cv2.createTrackbar('highS','Camera', high_saturation, 255, nothing)
    cv2.createTrackbar('lowV', 'Camera', low_value, 255, nothing)
    cv2.createTrackbar('highV', 'Camera', high_value, 255, nothing)

    cv2.createTrackbar('Area Threshold', 'Camera', areaThreshold, 100, nothing)
    cv2.createTrackbar('Aspect Ratio Min (%)', 'Camera', aspectRatioMin, 500, nothing)
    cv2.createTrackbar('Aspect Ratio Max (%)', 'Camera', aspectRatioMax, 500, nothing)
    cv2.createTrackbar('Solidity Threshold (%)', 'Camera', solidityThreshold, 100, nothing)
    cv2.createTrackbar('Polygon Approx Accuracy (%)', 'Camera', polygonApproxAccuracy, 10, nothing)

def location_y_to_distance(locationY):
    return locationY**2 / 1667 - locationY * 0.645079 + 228

def main():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    frame = cv2.resize(frame, (camera_width, camera_height))
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    init_trackbars()

    if enable_networking:
        netTable = connect_to_roborio()
    
    prev_time = dt.datetime.now()
    fps_display_time = 5
    i = 0

    while True:
        locationX, locationY = analyze_image(cap)
        if locationX == -1 and locationY == -1:
            distance = 0
            angle = 0
        else:
            distance = location_y_to_distance(locationY)
            angle = -camera_fov * (2 * (locationX / camera_width) - 1)

        if show_debug:
            print('{0:.2f} inches, {1:.2f} degress '.format(distance, angle))

        if enable_networking:
            toSend = [distance, angle]
            netTable.putNumberArray('Py Info', toSend)

            # Check if we are disconnected to roborio, and if so reconnect
            if not NetworkTables.isConnected():
                print('Lost connection to roborio.')
                netTable = connect_to_roborio()
        
        # Calculate FPS
        current_time = dt.datetime.now()
        time_delta = (current_time - prev_time).seconds
        i = i +1
        if time_delta >= fps_display_time:
            print("FPS: {0:.2f}".format(i / time_delta))
            prev_time = current_time
            i = 0

        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
