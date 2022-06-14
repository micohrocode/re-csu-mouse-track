import cv2 as cv
import numpy as np

# video capure
capture = cv.VideoCapture(0)
l_b=np.array([10,100,20])# lower hsv bound for orange
u_b=np.array([25,255,255])# upper hsv bound to orange
while True:
    ret, frame = capture.read()
    
    #constructs the foreground mask
    hsv=cv.cvtColor(frame,cv.COLOR_BGR2HSV)
    mask=cv.inRange(hsv,l_b,u_b)
    _, mask = cv.threshold(mask, 254, 255, cv.THRESH_BINARY)
    
    #finds desired contours
    fg_mask = mask
    contours, hierarchy = cv.findContours(fg_mask,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)[-2:]
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
 
    cv.imshow("Camera", frame)
    cv.imshow("Mask", mask)
    
    if cv.waitKey(20) & 0xFF==ord('q'):
        break
    
capture.release()
cv.destroyAllWindows()