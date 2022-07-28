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
    sizeMM = sizeMM * 25.4
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
    

    if side == 'right':
        return canvas.create_rectangle(
        int(x_center +(amp - halfWidth)),
        int(y_center +(window_h*height)),
        int(x_center +(amp + halfWidth)),
        int(y_center -(window_h*height)),
        outline="#fb0",
        fill="#fb0",
        state=showing)
    elif side == 'left':
        return canvas.create_rectangle(
        int(x_center -(amp - halfWidth)),
        int(y_center +(window_h*height)),
        int(x_center -(amp + halfWidth)),
        int(y_center -(window_h*height)),
        outline="#fb0",
        fill="#fb0",
        state=showing)


def cursor_collision(canvas,target,oval):
    xo, yo, xo2, yo2 = canvas.coords(oval)
    x1sr, y1sr, x2sr, y2sr = canvas.coords(target)
    if xo >= x1sr and yo >= y1sr and xo2 <= x2sr and yo2 <= y2sr:
        canvas.itemconfig(target, fill='green')
        return True


def main(sval1,sval2,svalY1, svalY2, my_w,name, inch, amp, targetWidth ,fileName, cursorVisible, interT, numT, camera, itemWidth):
    outR = 0
    outL = 0
    # variables above see if rectangles r out

    start_check_move = False
    in_center = False
    workbook = xlsxwriter.Workbook(fileName)
    outSheet = workbook.add_worksheet()
    my_w_child=Toplevel(my_w) # Child window
   
    window_width= my_w_child.winfo_screenwidth()              
    window_height= my_w_child.winfo_screenheight()              
    my_w_child.geometry("%dx%d" % (window_width,  window_height))
   
    my_w_child.title("Trial")
    myCanvas = Canvas(my_w_child,height=window_height,width=window_width)
    myCanvas.pack()
   
    l_b=np.array([sval1,svalY1,20])# lower hsv bound for orange
    u_b=np.array([sval2,svalY2,255])# upper hsv bound to orange
   
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
   
    # rect to start with
    choose_rect = random.uniform(0, 1)

    # external
    video = cv2.VideoCapture(camera, cv2.CAP_DSHOW)

    # value to convert pixel distance to millimeters check
    pixelToMM = False
   
    # continue until a value to convert is found
    while not pixelToMM:
        _, frame=video.read()
        pixelToMM = calibrate(frame, itemWidth ,l_b,u_b)
       
    print('Pixels per mm: '+ str(pixelToMM))
   
    # set movement velocity threshold, camera fps
    pixel_vel_thresh = math.ceil(math.ceil((inch/25.4) * 30) / 60)
    print('Vel pixel thresh: '+str(pixel_vel_thresh))
    oldTimeCheck = 0
    time.sleep(5)
    cell = 1
   
     # find center point
    window_center_x = window_width / 2
    window_center_y = window_height / 2
   
    while True:
        if numTrials == numT:
            break
        
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
        
        if outR == 0 and outL == 0:
            cursorOval = myCanvas.create_oval(x0, y0, x1, y1)
        else:
            if cursorVisible:
                cursorOval = myCanvas.create_oval(x0, y0, x1, y1)
            else:
                cursorOval = myCanvas.create_oval(x0, y0, x1, y1, state = 'hidden')



        if outR == 0 and outL == 0:
            if start_counter == 0:
                myCanvas.create_text(300, 50, text="Go to Center", fill="black", font=('Rockwell 30 bold'))
            else:
                countdown = "Stay Still for " + str(start_counter) + " Seconds"
                myCanvas.create_text(300, 50, text=countdown, fill="black", font=('Rockwell 30 bold'))


        start_check_move= cursor_collision(myCanvas,start_center_move, cursorOval)
        in_center = start_check_move
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
                    has_been_to_start = True
                    start_counter = 0
                    oldTimeCheck = 0

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
                        excel_side = None
                        if outR:
                            excel_side = 'right'
                        elif outL:
                            excel_side = 'left'
                        movements.append([start,end,math.dist(start, end)/pixelToMM/25.4,(end_time - start_time),move_portions,start_time, math.dist(start, end)/pixelToMM,hit_or_miss,target_center,math.dist(end, target_center),excel_side])
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
        #get rid of this section eventully
        else:
            cv2.putText(frame,'Place in center: ' + str(start_counter),(100,100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        cv2.imshow('Tracking',frame)
        cv2.setWindowProperty("Tracking", cv2.WND_PROP_TOPMOST, 1)
        if cv2.waitKey(20) & 0xFF==ord('p'):
            break
 
   
    for x in range(len(movements)):
        # start point to end point line
        x1, y1 = [movements[x][0][0], movements[x][1][0]], [movements[x][0][1], movements[x][1][1]]
        plt.plot(x1, y1, marker = 'o', label= f"line {x} {movements[x][3]}")
       
        # plot move portions for each movement
        for y in range(len(movements[x][4])):
            if y == 0:
                # velocity
                velocity = (math.dist((movements[x][4][y][0],movements[x][4][y][1]),start))/(movements[x][4][y][2].microseconds*0.000001) / pixelToMM / 25.4
                movements[x][4][y].append(velocity)
            else:
                # velocity
                velocity = (math.dist((movements[x][4][y][0],movements[x][4][y][1]),(movements[x][4][y-1][0],movements[x][4][y-1][1])))/(movements[x][4][y][2].microseconds*0.000001) / pixelToMM / 25.4
                movements[x][4][y].append(velocity)
                # acceleration
                accerlation = ((velocity - movements[x][4][y-1][3])/(movements[x][4][y][2].microseconds*0.000001))
                movements[x][4][y].append(accerlation)
            plt.plot(movements[x][4][y][0], movements[x][4][y][1], marker = 'o',color='k')
     
    # excel sheet organization
    outSheet.write("A1","Target Width: " + str(targetWidth))
    outSheet.write("B1","Amplitude: " + str(amp))
    outSheet.write("C1","Intertrial Interval: " + str(interT))
    outSheet.write("D1","# of Trials: " + str(numT))
    if cursorVisible:
        outSheet.write("E1","Cursor Visible: Yes")
    else:
        outSheet.write("E1","Cursor Visible: No")

    outSheet.write("A3","Trial")
    outSheet.write("B3","Start")
    outSheet.write("C3","End")
    outSheet.write("D3","Distance")
    outSheet.write("E3","Total Time")
# =============================================================================
#     outSheet.write("F3","Moves")
#     outSheet.write("G3","Time Of")
#     outSheet.write("H3","MM Traveled")
# =============================================================================
    outSheet.write("F3","Target Hit")
    outSheet.write("G3","Target Center")
    outSheet.write("H3","Distance From Center")
    outSheet.write("I3","Side")
   
   
    excel_place = 3
   
    # look at how to display movement data
    for i in range(len(movements)):
        hold_place = i + excel_place


        # testing new output
        outSheet.write(hold_place+1,0,str(i))
        outSheet.write(hold_place+1,1,str(movements[i][0]))
        outSheet.write(hold_place+1,2,str(movements[i][1]))
        outSheet.write(hold_place+1,3,str(movements[i][2]))
        outSheet.write(hold_place+1,4,str(movements[i][3]))
        outSheet.write(hold_place+1,5,str(movements[i][7]))
        outSheet.write(hold_place+1,6,str(movements[i][8]))
        outSheet.write(hold_place+1,7,str(movements[i][9]))
        outSheet.write(hold_place+1,8,str(movements[i][10]))
        
        outSheet.write(hold_place+3,0,'Trial')
        outSheet.write(hold_place+3,1,'Start')
        outSheet.write(hold_place+3,2,'End')
        outSheet.write(hold_place+3,3,'Dist')
        outSheet.write(hold_place+3,4,'Time')
        outSheet.write(hold_place+3,5,'Vel')
        outSheet.write(hold_place+3,6,'Accel')
        
        # movements
        for j in range(len(movements[i][4])):
            if (len(movements[i][4][j]))<=4 :
                # trial
                outSheet.write(hold_place+j+4,0,str(i))
                # start
                outSheet.write(hold_place+j+4,1,str(movements[i][0]))
                # end
                outSheet.write(hold_place+j+4,2,str((movements[i][4][j][0],movements[i][4][j][1])))
                # dist
                outSheet.write(hold_place+j+4,3,str(math.dist(movements[i][0],(movements[i][4][j][0],movements[i][4][j][1]))/pixelToMM/25.4))
                # time
                outSheet.write(hold_place+j+4,4,str(movements[i][5]+movements[i][4][j][2]))
                # vel
                outSheet.write(hold_place+j+4,5,str(movements[i][4][j][3]))
            else:
                # trial
                outSheet.write(hold_place+j+4,0,str(i))
                # start
                outSheet.write(hold_place+j+4,1,str((movements[i][4][j-1][0],movements[i][4][j-1][1])))
                # end
                outSheet.write(hold_place+j+4,2,str((movements[i][4][j][0],movements[i][4][j][1])))
                # dist
                outSheet.write(hold_place+j+4,3,str(math.dist((movements[i][4][j-1][0],movements[i][4][j-1][1]),(movements[i][4][j][0],movements[i][4][j][1]))/pixelToMM/25.4))
                # time
                outSheet.write(hold_place+j+4,4,str(movements[i][5]+movements[i][4][j][2]))
                # vel
                outSheet.write(hold_place+j+4,5,str(movements[i][4][j][3]))
                # accel
                outSheet.write(hold_place+j+4,6,str(movements[i][4][j][4]))
            excel_place = excel_place + 1
            
        excel_place = excel_place + len(movements[i][4][j])

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