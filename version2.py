import cv2
import numpy as np
import win32api, ctypes
from datetime import datetime
import pyautogui
import math
import matplotlib.pyplot as plt

#counter for tracking every number of frames
counter = 0

fig, ax1 = plt.subplots()


plt.xlim(0 , 640)
plt.ylim(0  ,480)
tracker = cv2.TrackerMIL_create()
#returns true if there is an error/no frame was detected 
def detect(frame):
    l_b=np.array([85,0,20])# lower hsv bound for orange
    u_b=np.array([95,255,255])# upper hsv bound to orange

    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,l_b,u_b)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    #finds desired contours
    
    fg_mask = mask
    cv2.imshow('mask',fg_mask)
    contours, _ = cv2.findContours(fg_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2:]
    areas = [cv2.contourArea(c) for c in contours]
    if len(areas) < 1:
        return (-1,-1,-1,-1), True 
    max_index = np.argmax(areas)
    # Draw the bounding box
    cnt = contours[max_index]
    x,y,w,h = cv2.boundingRect(cnt)
    return (x,y,w,h), False

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
# pixel velocity threshold
pixel_vel_thresh = 20

video = cv2.VideoCapture(1, cv2.CAP_DSHOW)
while True:
    _, frame=video.read()
    frame = cv2.flip(frame, -1)
    bbox,err  = detect(frame)
    if err:
        continue
    else:
        break

ok = tracker.init(frame,bbox)


while True:
    if counter == 1:
        while True:
            _, frame=video.read()
            frame = cv2.flip(frame, -1)

            bbox,err  = detect(frame)
            if err:
                continue
            else:
                break
        tracker = cv2.TrackerMIL_create()
        ok = tracker.init(frame,bbox)
        counter = 0

    _, frame=video.read()
    frame = cv2.flip(frame, -1)

    ok,bbox=tracker.update(frame)
    if ok:
        (x,y,w,h)=[int(v) for v in bbox]
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2,1)
        x2 = x + int(w/2)
        cv2.circle(frame,(x2,y),4,(0,0,255),-1)
        
        # MOVE INFO FOUND HERE 
        # TRYING TO FIND THE START AND END OF A MOVEMENT
        if not prev:
            # set orginal check point for movement
            prev = (x2,y)
            status = "still"
        else:
            if prev[0] > x2+pixel_vel_thresh or prev[0] <x2-pixel_vel_thresh:
                # if moving in x direction
                frame = cv2.putText(frame, 'Moving', (x,y), cv2.FONT_HERSHEY_TRIPLEX, 
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
            elif prev[1] > y+pixel_vel_thresh or prev[1] <y-pixel_vel_thresh:
                # if moving in the y direction
                frame = cv2.putText(frame, 'Moving', (x,y), cv2.FONT_HERSHEY_TRIPLEX, 
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
            elif (prev[0] < x2+pixel_vel_thresh or prev[0] >x2-pixel_vel_thresh) and (prev[1] < y+pixel_vel_thresh or prev[1] >y-pixel_vel_thresh):
                # if not moving enough to count as a movement, ie stopped or slowing down
                frame = cv2.putText(frame, 'Still', (x,y), cv2.FONT_HERSHEY_TRIPLEX, 
                        1, (0,255,0), 2)
                
                # if it was in a movement, stop the movement and log the information
                if status == "moving":
                    end = (x2,y)
                    end_time = datetime.now()
                    movements.append([start,end,math.dist(start, end),(end_time - start_time),move_portions,start_time.microsecond])
                    move_portions = []
                    start_time = None
                
                status = "still"
        
        
        # ctypes.windll.user32.SetCursorPos(x2, y)  
        # plt.plot(x2, y, 'ro')

    else:
        cv2.putText(frame,'Error',(100,100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    cv2.imshow('Tracking',frame)
    cv2.setWindowProperty("Tracking", cv2.WND_PROP_TOPMOST, 1)
    if cv2.waitKey(20) & 0xFF==ord('p'):
       break
    counter = counter + 1
    
print(movements)

for x in range(len(movements)):
    # start point to end point line
    x1, y1 = [movements[x][0][0], movements[x][1][0]], [movements[x][0][1], movements[x][1][1]]
    plt.plot(x1, y1, marker = 'o', label= f"line {x} {movements[x][3]}")
    
    for y in range(len(movements[x][4])):
        plt.plot(movements[x][4][y][0], movements[x][4][y][1], marker = 'o',color='k')

plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
ax1.invert_yaxis()
video.release()
cv2.destroyAllWindows()