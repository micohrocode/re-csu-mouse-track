import cv2
import numpy as np
from datetime import datetime
import time
import math
import matplotlib.pyplot as plt
import xlsxwriter
from tkinter import *
import random

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
def draw_rectangle(canvas,x_center,y_center,window_w,window_h,height,side, inch, amp, targetWidth, showing):
   
    halfWidth = targetWidth/2 * inch
    amp = amp * inch
    halfAmp = amp/2

    if side == 'right':
        return canvas.create_rectangle(
        int(x_center +(halfAmp - halfWidth)),
        int(y_center +(window_h*height)),
        int(x_center +(halfAmp + halfWidth)),
        int(y_center -(window_h*height)),
        outline="#fb0",
        fill="#fb0",
        state=showing)

    elif side == 'left':
        return canvas.create_rectangle(
        int(x_center -(halfAmp - halfWidth)),
        int(y_center +(window_h*height)),
        int(x_center -(halfAmp + halfWidth)),
        int(y_center -(window_h*height)),
        outline="#fb0",
        fill="#fb0",
        state=showing)

   
def cursor_collision(canvas,coords,active,target):
    coll = canvas.find_overlapping(coords[0],
                         coords[1],
                         coords[2],
                         coords[3])
   
    coll = list(coll)
    if len(coll) >= active:
        canvas.itemconfig(target, fill='green')
        return True

def main(sval1,sval2,my_w,name, inch, amp, targetWidth ,fileName, cursorVisible, interT, numT):
    outR = 0
    outL = 0
    # variables above see if rectangles r out
    workbook = xlsxwriter.Workbook(fileName)
    outSheet = workbook.add_worksheet()
    my_w_child=Toplevel(my_w) # Child window
   
    window_width= my_w_child.winfo_screenwidth()              
    window_height= my_w_child.winfo_screenheight()              
    my_w_child.geometry("%dx%d" % (window_width,  window_height))
   
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
    plt.xlim(0 , 1920)
    plt.ylim(0  ,1080)

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
    pixel_vel_thresh = 3
   
    # check that it has been to the center
    has_been_to_start = False
    start_counter = 0
   
    numTrials = 0
    
    # check if rect should change
    # free_to_switch = True
   
    # rect to start with
    choose_rect = random.uniform(0, 1)

    # external
    video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # build in
    # video = cv2.VideoCapture(0)
   
    # value to convert pixel distance to millimeters check
    pixelToMM = False
   
    # continue until a value to convert is found
    while not pixelToMM:
        _, frame=video.read()
        pixelToMM = calibrate(frame, 76.2,l_b,u_b)
       
    print('Pixels per mm: '+ str(pixelToMM))
   
    # set movement velocity threshold, camera fps
    pixel_vel_thresh = math.ceil(math.ceil((inch/25.4) * 30) / 60)
    print('Vel pixel thresh: '+str(pixel_vel_thresh))
    oldTimeCheck = 0
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
     # find center point
    window_center_x = window_width / 2
    window_center_y = window_height / 2
   
    while True:
        if numTrials == numT:
            break
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
        
        # cursor location
        (x,y,w,h)=[int(v) for v in bbox]
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2,1)
        x2 = x + int(w/2)
        cv2.circle(frame,(x2,y),4,(0,0,255),-1)
        
        y_hold = y
        
        x2 = int(x2*(inch/(pixelToMM*25.4)))
        y = int(y*(inch/(pixelToMM*25.4)))
        
        # clear canvas for updating
        myCanvas.delete(ALL)
        
        
        
        # rectangle area drawing
        if outR == 1:
            rectangleR = draw_rectangle(myCanvas, window_center_x, window_center_y, window_width, window_height,.4, 'right', inch, amp, targetWidth, 'normal')
        elif outL == 1:
            rectangleL = draw_rectangle(myCanvas, window_center_x, window_center_y, window_width, window_height, .4,  'left', inch, amp, targetWidth,'normal')
        else:
            rectangleR = draw_rectangle(myCanvas, window_center_x, window_center_y, window_width, window_height,.4, 'right', inch, amp, targetWidth,'hidden')
            rectangleL = draw_rectangle(myCanvas, window_center_x, window_center_y, window_width, window_height, .4,  'left', inch, amp, targetWidth,'hidden')

        # cursor updating/drawing
        r = 5
        x0 = x2 - r
        y0 = y - r
        x1 = x2 + r
        y1 = y + r
        
        
        # center start position
        start_center_move = myCanvas.create_rectangle(int(window_center_x - 25),
                                int(window_center_y - 25),
                                int(window_center_x + 25),
                                int(window_center_y + 25),
                                outline="black",
                                fill="red")
        
        cursorOval = myCanvas.create_oval(x0, y0, x1, y1)
        if outR == 0 and outL == 0:
            if start_counter == 0:
                myCanvas.create_text(300, 50, text="Go to Center", fill="black", font=('Helvetica 30 bold'))
            else:
                countdown = "Stay Still for " + str(start_counter) + " Seconds"
                myCanvas.create_text(300, 50, text=countdown, fill="black", font=('Helvetica 30 bold'))


        start_check_move = cursor_collision(myCanvas,myCanvas.coords(start_center_move),2,start_center_move)
        
        my_w_child.update()
        
        if not start_check_move:
            start_counter = 0
            oldtime = time.time()
            oldTimeCheck = 1
        else:
            if oldTimeCheck == 0:
                oldtime = time.time()
                oldTimeCheck = 1
            else:
                elapsed = time.time() - oldtime
                start_counter = interT - int(elapsed)
                if elapsed >= interT:
                   #print(elapsed)
                    has_been_to_start = True
                    start_counter = 0
                    oldTimeCheck = 0
                    # choose_rect = random.uniform(0, 1)
                        
        # # after they are in the start for long enough check if they leave the start to start move?
        in_center  = cursor_collision(myCanvas,myCanvas.coords(start_center_move),2,start_center_move)
            
        if has_been_to_start:
            
            if cursorVisible == 0:
                myCanvas.itemconfigure(cursorOval, state = 'hidden')

            if choose_rect >= .5:
                myCanvas.itemconfigure(rectangleR, state='normal')
                outR = 1
            else:
                myCanvas.itemconfigure(rectangleL, state='normal')
                outL = 1
            my_w_child.update()
            
            # movement checks/data
            if not prev:
                # set orginal check point for movement
                prev = (x2,y)
                status = "still"
            elif not in_center:
                if prev[0] > x2+pixel_vel_thresh or prev[0] <x2-pixel_vel_thresh and not in_center:
                    # if moving in x direction
                    frame = cv2.putText(frame, 'Moving', (x,y_hold), cv2.FONT_HERSHEY_TRIPLEX,
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
                elif prev[1] > y+pixel_vel_thresh or prev[1] <y-pixel_vel_thresh and not in_center:
                    # if moving in the y direction
                    frame = cv2.putText(frame, 'Moving', (x,y_hold), cv2.FONT_HERSHEY_TRIPLEX,
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
                    frame = cv2.putText(frame, 'Still', (x,y_hold), cv2.FONT_HERSHEY_TRIPLEX,
                            1, (0,255,0), 2)
                    
                    # if it was in a movement, stop the movement and log the information
                    if status == "moving":
                        # stopping point to target?
                        hit_or_miss = 'miss'
                        target_center = None
                        
                        x1o, y1o, x2o, y2o = myCanvas.coords(cursorOval)
                        if choose_rect >= .5:
                            x1r, y1r, x2r, y2r = myCanvas.coords(rectangleR)
                            target_center = (((x2r+x1r)/2),((y1r+y2r)/2))
                            if x1o >= x1r and y1o >= y1r and x2o <= x2r and y2o <= y2r:
                                myCanvas.itemconfig(rectangleR, fill='green')
                                hit_or_miss = 'hit'
                                my_w_child.update()
                        else:
                            x1r, y1r, x2r, y2r = myCanvas.coords(rectangleL)
                            target_center = (((x2r+x1r)/2),((y1r+y2r)/2))
                            if x1o >= x1r and y1o >= y1r and x2o <= x2r and y2o <= y2r:
                                myCanvas.itemconfig(rectangleL, fill='green')
                                hit_or_miss = 'hit'
                                my_w_child.update()
                        
                        end = (x2,y)
                        end_time = datetime.now()
                        movements.append([start,end,math.dist(start, end),(end_time - start_time),move_portions,start_time, math.dist(start, end)/pixelToMM,hit_or_miss,target_center,math.dist(end, target_center)])
                        move_portions = []
                        start_time = None
                        # start new test at the end of each move
                        has_been_to_start = False
                        outR = 0
                        outL = 0
                        status = "still"
                        choose_rect = random.uniform(0, 1)
                        numTrials = numTrials + 1
                        continue
                    
                    status = "still"

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
    outSheet.write("H1","Target Hit")
    outSheet.write("I1","Target Center")
    outSheet.write("J1","Distance From Center")
   
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
        outSheet.write(i+1,7,str(movements[i][7]))
        outSheet.write(i+1,8,str(movements[i][8]))
        outSheet.write(i+1,9,str(movements[i][9]))
        excel_place = excel_place + 1


    outSheet.write(excel_place+1, 0, "Subject Code:")
    outSheet.write(excel_place+1, 1, name)
       
    # move order as plotted legend
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax1.invert_yaxis()
    video.release()
    cv2.destroyAllWindows()
    workbook.close()
    my_w_child.destroy()
if __name__ == "__main__":
    main()