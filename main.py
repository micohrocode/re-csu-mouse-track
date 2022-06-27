import cv2 as cv
import numpy as np
import win32api, ctypes
from datetime import datetime
import pyautogui
import math
import matplotlib.pyplot as plt


def maxContour(mask):
    #finds desired contours
    fg_mask = mask
    contours, _ = cv.findContours(fg_mask,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)[-2:]
    areas = [cv.contourArea(c) for c in contours]
    
    # If there are no countours
    if len(areas) < 1:
        return (0,0,0,0)
    else:
        # Finds largest object
        max_index = np.argmax(areas)
        
    # Draw the bounding box
    cnt = contours[max_index]
    x,y,w,h = cv.boundingRect(cnt)
    
    return (x,y,w,h)

def frameToColorMask(frame):
    # resize frame to size of monitor and flips image
    frame = cv.resize(frame, (win32api.GetSystemMetrics(0),win32api.GetSystemMetrics(1)), interpolation = cv.INTER_AREA)
    frame = cv.flip(frame,1)
  
    #constructs the foreground mask
    hsv=cv.cvtColor(frame,cv.COLOR_BGR2HSV)
    mask=cv.inRange(hsv,l_b,u_b)
    _, mask = cv.threshold(mask, 254, 255, cv.THRESH_BINARY)
    return frame,mask

#counter for tracking every number of frames
counter = 0

smooth = 2
prevX, prevY = 0, 0
curX, curY = 0, 0 
# video capure
capture = cv.VideoCapture(0)
l_b=np.array([85,100,20])# lower hsv bound for orange
u_b=np.array([95,255,255])# upper hsv bound to orange

# TESTING MOVEMENT DETECTION THRESHOLD
# check for movement
prev = None
# start and end of one detected move
start = None
end = None
# if currently moving
status = None
# all total movements captured
movements = []
# portions of movement
move_portions = []
# start and end time of current movement
start_time = None
end_time = None
# click sleep time check
click_timer = None

# create plots
fig, ax1 = plt.subplots()



ok, frame = capture.read()

frame,mask = frameToColorMask(frame)
(x,y,w,h) = maxContour(mask)
bbox = (x,y,w,h)
print('first'+str(bbox))

while True:
    ret, frame = capture.read()
    
    frame,mask = frameToColorMask(frame)
    
    # TRACKING FIXES?
    (x,y,w,h) = maxContour(mask)
    bbox = (x,y,w,h)
    print(bbox)  
      
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
            # get update point of movement and time since start
            if start_time:
                move_portions.append([x2,y,(datetime.now() - start_time)])
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
            # get update point of movement and time since start
            if start_time:
                move_portions.append([x2,y,(datetime.now() - start_time)])
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
                movements.append([start,end,math.dist(start, end),(end_time - start_time),move_portions,start_time.microsecond])
                move_portions = []
                start_time = None
            
            status = "still"
            
    if status == "still" and not click_timer:
        click_timer = datetime.now()
        
    if status == "still" and (datetime.now()-click_timer).seconds >= 2:
        pyautogui.click()
        click_timer = None
        
    if status == "moving":
        click_timer = None
  
    # smooths cursor
    curX = int(prevX + (x2-prevX)/smooth)
    curY = int(curY + ((y+30)-prevY)/smooth)
    prevX = curX
    prevY = curY

    
    ctypes.windll.user32.SetCursorPos(curX, curY)  
    cv.imshow("Camera", frame)
    #cv.setWindowProperty("Camera", cv.WND_PROP_TOPMOST, 1)
    cv.imshow("Mask", mask)
    
    for x in range(len(movements)):
        # start point to end point line
        x1, y1 = [movements[x][0][0], movements[x][1][0]], [movements[x][0][1], movements[x][1][1]]
        plt.plot(x1, y1, marker = 'o', label= f"line {x} {movements[x][3]}")
        
        # parts of the main move from start to end
        #print(movements[x][3].seconds,movements[x][3].microseconds)
        #print(([z[2] for z in movements[x][4]]))
        #print(movements[x])
        for y in range(len(movements[x][4])):
            # x velocity?
            if y == 0:
                pass
                # print("x pixels per microsecond:")
                # print((movements[x][4][y][0]-movements[x][5])/movements[x][4][y][2].microseconds)
            else:
                pass
                # print("x pixels per microsecond:")
                # print((movements[x][4][y][0]-movements[x][4][y-1][0])/movements[x][4][y][2].microseconds)
            plt.plot(movements[x][4][y][0], movements[x][4][y][1], marker = 'o',color='k')
    
    if cv.waitKey(20) & 0xFF==ord('p'):
        break
    
# show line order with legen
#plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
ax1.invert_yaxis()
capture.release()
cv.destroyAllWindows()   