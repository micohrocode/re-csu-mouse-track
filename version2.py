import cv2
import numpy as np
import win32api, ctypes
from datetime import datetime
import time
import pyautogui
import math
import matplotlib.pyplot as plt
import xlsxwriter
from tkinter import *

workbook = xlsxwriter.Workbook("data.xlsx")
outSheet = workbook.add_worksheet()

def pidInfo(name,place):
    outSheet.write(place+1, 0, "Name:")
    outSheet.write(place+1, 1, name)

def frameToColorMask(frame,l_b,u_b):
    #constructs the foreground mask from color values
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,l_b,u_b)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    return frame,mask

def contourAreas(mask):
    #finds desired contours that match color range
    fg_mask = mask
    contours, _ = cv2.findContours(fg_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2:]
    # area size of eatch matching contour
    areas = [cv2.contourArea(c) for c in contours]
    return areas, contours

def detect(frame,l_b,u_b):
    frame,mask = frameToColorMask(frame,l_b,u_b)
    areas, contours = contourAreas(mask)
   
    # no areas then send error
    if len(areas) < 1:
        return (-1,-1,-1,-1), True
    max_index = np.argmax(areas)
    # Draw the bounding box
    cnt = contours[max_index]
    x,y,w,h = cv2.boundingRect(cnt)
    return (x,y,w,h), False

def calibrate(frame,sizeMM,l_b,u_b):
    frame,mask = frameToColorMask(frame,l_b,u_b)
    areas, contours = contourAreas(mask)
   
    # no areas found
    if len(areas) < 1:
        return False
    max_index = np.argmax(areas)
    # Draw the bounding box
    cnt = contours[max_index]
    x,y,w,h = cv2.boundingRect(cnt)
   
    # value to convert pixels to millimeters
    pixelPerMM = w/sizeMM
   
    return pixelPerMM

def draw_rectangle(canvas,x_center,y_center,window_w,window_h,amplitude,thickness,height,side):
    if side == 'right':
        return canvas.create_rectangle(
        int(x_center +(window_w*amplitude)), 
        int(y_center +(window_h*height)), 
        int(x_center +(window_w*(amplitude+thickness))), 
        int(y_center -(window_h*height)),
        outline="#fb0",
        fill="#fb0")
    elif side == 'left':
        return canvas.create_rectangle(
        int(x_center -(window_w*(amplitude+thickness))), 
        int(y_center +(window_h*height)), 
        int(x_center -(window_w*amplitude)), 
        int(y_center -(window_h*height)),
        outline="#fb0",
        fill="#fb0")
   
def cursor_collision(canvas,coords,active,target):
    coll = canvas.find_overlapping(coords[0],
                         coords[1], 
                         coords[2], 
                         coords[3])
    
    coll = list(coll)
    if len(coll) >= active:
        canvas.itemconfig(target, fill='green')
        return True

def main(sval1,sval2,my_w,name, rectW):
    my_w_child=Toplevel(my_w) # Child window 
    
    window_width = 640 * 2
    window_height = 480 * 2
    my_w_child.geometry(str(window_width)+"x"+str(window_height))  # Size of the window 
    my_w_child.title("Cursor Test")
    myCanvas = Canvas(my_w_child,height=window_height,width=window_width)
    myCanvas.pack()
    
    
    
    l_b=np.array([sval1,0,20])# lower hsv bound for orange
    u_b=np.array([sval2,255,255])# upper hsv bound to orange
   
    #counter for tracking every number of frames
    counter = 0

    # movement graphs
    fig, ax1 = plt.subplots()

    # limit plot to webcam video res size
    plt.xlim(0 , 640)
    plt.ylim(0  ,480)

    tracker = cv2.TrackerCSRT_create()
   
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
    
    # check that it has been to the center
    has_been_to_start = False
    start_counter = 0

    # external
    video = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    # build in
    # video = cv.VideoCapture(0)
   
    # value to convert pixel distance to millimeters check
    pixelToMM = False
   
    # continue until a value to convert is found
    while not pixelToMM:
        _, frame=video.read()
        pixelToMM = calibrate(frame, 76.2,l_b,u_b)
       
    print('Pixels per mm: '+ str(pixelToMM))
       
    time.sleep(5)
    cell = 1
    while True:
        _, frame=video.read()
       
        bbox,err  = detect(frame,l_b,u_b)
        if err:
            continue
        else:
            break
        frame = cv2.flip(frame, -1)
   
    tracker.init(frame,bbox)
   
    while True:
        if counter == 1:
            while True:
                _, frame=video.read()
                frame = cv2.flip(frame, -1)
   
                bbox,err  = detect(frame,l_b,u_b)
                if err:
                    continue
                else:
                    break
            tracker = cv2.TrackerCSRT_create()
            tracker.init(frame,bbox)
            counter = 0
   
        _, frame=video.read()
        frame = cv2.flip(frame, -1)
   
        ok,bbox=tracker.update(frame)
        if ok:
            # cursor location
            (x,y,w,h)=[int(v) for v in bbox]
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2,1)
            x2 = x + int(w/2)
            cv2.circle(frame,(x2,y),4,(0,0,255),-1)
            
            # clear canvas for updating
            myCanvas.delete(ALL)
            
            # find center point
            window_center_x = window_width / 2
            window_center_y = window_height / 2
            
            # rectangle area drawing
            rectangle1 = draw_rectangle(myCanvas, window_center_x, window_center_y, window_width, window_height, .25, .10, .40, 'right')
            rectangle2 = draw_rectangle(myCanvas, window_center_x, window_center_y, window_width, window_height, .25, .10, .40, 'left')
            
            # center target
            target = myCanvas.create_rectangle(int(window_center_x +(window_width*.25)),
                                 int(window_center_y +(window_height*.05)), 
                                 int(window_center_x +(window_width*.35)), 
                                 int(window_center_y -(window_height*.05)),
                                 outline="#fb0",
                                 fill="#fb0")
            
            # cursor updating/drawing
            r = 10
            x0 = ((x2/640)*window_width) - r
            y0 = ((y/480)*window_width) - r
            x1 = ((x2/640)*window_width) + r
            y1 = ((y/480)*window_width) + r
            myCanvas.create_oval(x0, y0, x1, y1)
            
            # collision detection
            cursor_collision(myCanvas,myCanvas.coords(target),3,target)
            
            # center start position
            start_center_move = myCanvas.create_rectangle(int(window_center_x - 25),
                                 int(window_center_y - 25), 
                                 int(window_center_x + 25), 
                                 int(window_center_y + 25),
                                 outline="black",
                                 fill="red")
            
            
            start_check_move = cursor_collision(myCanvas,myCanvas.coords(start_center_move),2,start_center_move)
            
            my_w_child.update()
            
            if not start_check_move:
                start_counter = 0
            else:
                start_counter = start_counter + 1
                if start_counter >= 5:
                    has_been_to_start = True
                    start_counter = 0
            
            if has_been_to_start:
                # movement checks/data
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
                            movements.append([start,end,math.dist(start, end),(end_time - start_time),move_portions,start_time, math.dist(start, end)/pixelToMM])
                            move_portions = []
                            start_time = None
                            # start new test at the end of each move
                            has_been_to_start = False
                            status = "still"
                            continue
                       
                        status = "still"
                # outSheet.write(cell, 0, x2)
                # outSheet.write(cell, 1, y)
                # cell = cell + 1
            else:
                cv2.putText(frame,'Place in center: ' + str(start_counter),(100,100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
            cv2.imshow('Tracking',frame)
            cv2.setWindowProperty("Tracking", cv2.WND_PROP_TOPMOST, 1)
            if cv2.waitKey(20) & 0xFF==ord('p'):
               break
            counter = counter + 1
   
    for x in range(len(movements)):
        # start point to end point line
        x1, y1 = [movements[x][0][0], movements[x][1][0]], [movements[x][0][1], movements[x][1][1]]
        plt.plot(x1, y1, marker = 'o', label= f"line {x} {movements[x][3]}")
       
        # plot move portions for each movement
        for y in range(len(movements[x][4])):
            if y == 0:
                # velocity
                velocity = (math.dist((movements[x][4][y][0],movements[x][4][y][1]),start))/(movements[x][4][y][2].microseconds*0.000001) / pixelToMM
                movements[x][4][y].append(velocity)
            else:
                # velocity
                velocity = (math.dist((movements[x][4][y][0],movements[x][4][y][1]),(movements[x][4][y-1][0],movements[x][4][y-1][1])))/(movements[x][4][y][2].microseconds*0.000001) / pixelToMM
                movements[x][4][y].append(velocity)
                # acceleration
                accerlation = ((velocity - movements[x][4][y-1][3])/(movements[x][4][y][2].microseconds*0.000001))
                movements[x][4][y].append(accerlation)
            plt.plot(movements[x][4][y][0], movements[x][4][y][1], marker = 'o',color='k')
      
    # excel sheet organization
    outSheet.write("A1","Start")
    outSheet.write("B1","End") 
    outSheet.write("C1","Distance")
    outSheet.write("D1","Total Time") 
    outSheet.write("E1","Moves")
    outSheet.write("F1","Time Of")
    outSheet.write("G1","MM Traveled")
    
    excel_place = 0
    
    # look at how to display movement data
    for i in range(len(movements)):
        outSheet.write(i+1,0,str(movements[i][0]))
        outSheet.write(i+1,1,str(movements[i][1]))
        outSheet.write(i+1,2,str(movements[i][2]))
        outSheet.write(i+1,3,str(movements[i][3]))
        outSheet.write(i+1,4,str(movements[i][4]))
        outSheet.write(i+1,5,str(movements[i][5]))
        outSheet.write(i+1,6,str(movements[i][6]))
        excel_place = excel_place + 1
    
    pidInfo(name,excel_place)
    
        
    # move order as plotted legend
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax1.invert_yaxis()
    video.release()
    cv2.destroyAllWindows()
    workbook.close()
if __name__ == "__main__":
    main()