import cv2 as cv
import numpy as np
from tracker import Tracker

'''
TODO/IDEAS:
create class to keep id of boxes that are moving?
keep track of highest box's highest point, even if box disapears, select the next highest box?
mouse movent can update as highest box updates
improve detection, remove hand issues for too many boxes problem?
no bounding box as dwell time for clicks?
mouse moves well up and down, but may drift if it reaches the end, stop with experimental walls?
'''

# video capure
capture = cv.VideoCapture(0)

l_b=np.array([10,100,20])# lower hsv bound for orange
u_b=np.array([25,255,255])# upper hsv bound to orange

while True:
    ret, frame = capture.read()
    #height, width = frame.shape[:2]
    
    # re color image to hsv for 
    hsv=cv.cvtColor(frame,cv.COLOR_BGR2HSV)
    # remove colors from image that are not in range
    mask=cv.inRange(hsv,l_b,u_b)
    
    # clear out gray shadow values
    _, mask = cv.threshold(mask, 254, 255, cv.THRESH_BINARY)
    # find contours of mask
    contours , _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # bounding boxes found
    detections = []
    
    for cnt in contours:
        # calc area and remove unneeded elements
        area = cv.contourArea(cnt)
        if area > 50:
            # rect from contour
            x,y,w,h = cv.boundingRect(cnt)
            cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)
            # center top point of box
            cv.circle(frame,(int(x+w/2),y),3,(0,0,255),3)
            detections.append([x,y,w,h])
    

    cv.imshow("Camera", frame)
    cv.imshow("Mask", mask)
    
    if cv.waitKey(20) & 0xFF==ord('q'):
        break
    
capture.release()
cv.destroyAllWindows()