#imports (same as 2020 vision)
import math
import cv2
import numpy
from networktables import NetworkTables

#set up networkTables (connect to other code?)
NetworkTables.initialize(server='10.30.24.2')
netTable = NetworkTables.getTable('pi')

#capture video
video = cv2.VideoCapture(0)

#set up display windows
cv2.namedWindow('Camera', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('Edges', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("Mask", cv2.WINDOW_AUTOSIZE)

def nothing(x);
pass

#globals (outside of funtions)
ErrorCodes = {0; 'No error'}
ERROR = 0

#trackbars




while true:
    ERROR = 0


cap.release()
cv2.destroyAllWindows()
