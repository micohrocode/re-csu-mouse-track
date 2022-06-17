import cv2 as cv
import numpy as np
import win32api, win32con
from datetime import datetime
import math   

# video capure
capture = cv.VideoCapture(0)
l_b=np.array([0,100,20])# lower hsv bound for orange
u_b=np.array([10,255,255])# upper hsv bound to orange

# TESTING MOVEMENT DETECTION THRESHOLD
# check for movement
prev = None
# start and end of one detected move
start = None
end = None
# if currently moving
status = None
# all movements captured
movements = []
# start and end time of current movement
start_time = None
end_time = None
# click sleep time check
click_timer = None

while True:
    ret, frame = capture.read()
    
    # resize frame to size of monitor
    frame = cv.resize(frame, (win32api.GetSystemMetrics(0),win32api.GetSystemMetrics(1)), interpolation = cv.INTER_AREA)
    
    #constructs the foreground mask
    hsv=cv.cvtColor(frame,cv.COLOR_BGR2HSV)
    mask=cv.inRange(hsv,l_b,u_b)
    _, mask = cv.threshold(mask, 254, 255, cv.THRESH_BINARY)
    
    #finds desired contours
    fg_mask = mask
    contours, _ = cv.findContours(fg_mask,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)[-2:]
    areas = [cv.contourArea(c) for c in contours]
 
    # If there are no countours
    if len(areas) < 1:
        continue
    else:
        # Finds largest object
        max_index = np.argmax(areas)
 
    # Draw the bounding box
    cnt = contours[max_index]
    x,y,w,h = cv.boundingRect(cnt)
    cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)
        
    #draws circle on top of the point (index finger)
    x2 = x + int(w/2)
    cv.circle(frame,(x2,y),4,(0,255,0),-1)
    
    # TRYING TO FIND THE START AND END OF A MOVEMENT
    if not prev:
        # set orginal check point for movement
        prev = (x2,y)
        status = "still"
    else:
        if prev[0] > x2+20 or prev[0] <x2-20:
            # if moving in x direction
            frame = cv.putText(frame, 'Moving', (x,y), cv.FONT_HERSHEY_TRIPLEX, 
                    1, (0,255,0), 2)
            prev = (x2,y)
            
            # if it was still start a movement
            if status == "still":
                start  = (x2,y)
                start_time = datetime.now()
            
            status = "moving"
        elif prev[1] > y+20 or prev[1] <y-20:
            # if moving in the y direction
            frame = cv.putText(frame, 'Moving', (x,y), cv.FONT_HERSHEY_TRIPLEX, 
                    1, (0,255,0), 2)
            prev = (x2,y)
            
            # if it was still start a movement
            if status == "still":
                start  = (x2,y)
                start_time = datetime.now()
            
            status = "moving"
        elif (prev[0] < x2+20 or prev[0] >x2-20) and (prev[1] < y+20 or prev[1] >y-20):
            # if not moving enough to count as a movement, ie stopped or slowing down
            frame = cv.putText(frame, 'Still', (x,y), cv.FONT_HERSHEY_TRIPLEX, 
                    1, (0,255,0), 2)
            
            # if it was in a movement, stop the movement and log the information
            if status == "moving":
                end = (x2,y)
                end_time = datetime.now()
                movements.append([start,end,math.dist(start, end),(end_time - start_time).microseconds])
            
            status = "still"
            
    if status == "still" and not click_timer:
        print("here")
        click_timer = datetime.now()
        
    if status == "still" and (datetime.now()-click_timer).seconds >= 3:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        print("click")
        click_timer = None
        
    if status == "moving":
        print("moved")
        click_timer = None
    
    # move mouse to top of tracked color
    win32api.SetCursorPos((x2,y+30))
 
    cv.imshow("Camera", frame)
    #cv.imshow("Mask", mask)
    
    if cv.waitKey(20) & 0xFF==ord('p'):
        break
    
print(movements)
capture.release()
cv.destroyAllWindows()