import cv2 as cv
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

capture = cv.VideoCapture(0)

# object detector
object_detector = cv.createBackgroundSubtractorMOG2(history=100, varThreshold=40, detectShadows=False)

while True:
    ret, frame = capture.read()
    height, width = frame.shape[:2]
    
    # region of interest
    roi = frame[:200,:300] 
    
    # apply background subtraction mask to video
    mask = object_detector.apply(roi)
    # clear out gray shadow values
    _, mask = cv.threshold(mask, 254, 255, cv.THRESH_BINARY)
    # find contours of mask
    contours , _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # bounding boxes found
    detections = []
    
    tracker = Tracker()
    
    for cnt in contours:
        # calc area and remove unneeded elements
        area = cv.contourArea(cnt)
        if area > 50:
            #cv.drawContours(roi,[cnt],-1,(0,255,0),2)
            # rect from contour
            x,y,w,h = cv.boundingRect(cnt)
            cv.rectangle(roi,(x,y),(x+w,y+h),(0,255,0),3)
            # center top point of box
            cv.circle(roi,(int(x+w/2),y),3,(0,0,255),3)
            detections.append([x,y,w,h])
            print(detections)
    
    # check for detections
    if detections:
        tracker.update(detections,roi,width)
    cv.imshow("Camera", frame)
    cv.imshow("Mask", mask)
    cv.imshow("Roi", roi)
    
    if cv.waitKey(20) & 0xFF==ord('d'):
        break
    
capture.release()
cv.destroyAllWindows()