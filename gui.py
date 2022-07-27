from optparse import Option
from tkinter import *
from version2 import *
import numpy as np
from PIL import Image, ImageTk
from tkinter import filedialog
import cv2

root = Tk()
root.title('Data Acquistion')
sl_value = 10
window_width= root.winfo_screenwidth()               
window_height= root.winfo_screenheight()               
root.geometry("%dx%d" % (window_width,  window_height))
global fileCheck
fileCheck = 0 
def testCamera():
    video = cv2.VideoCapture(int(selected.get()), cv2.CAP_DSHOW)
    l_b=np.array([int(lowerXE.get()),int(lowerYE.get()),20])
    u_b=np.array([int(upperXE.get()),int(upperYE.get()),255])
    _, frame=video.read()
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,l_b,u_b)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    cv2.imshow("mask", mask)
   

def mainCV():
    cursor = 0
    lowerX = int(lowerXE.get())
    upperX = int(upperXE.get())
    lowerY = int(lowerYE.get())
    upperY = int(upperYE.get())
    camera = int(selected.get())
    subCode = pidE.get()
    interT = float(interTrialE.get())
    x0, y0, x1, y1 = canvas.coords(rectangle) 
    inch = x1-x0
    targetWidth = float(twEntry.get())
    amplitude = float(ampEntry.get())
    numT = int(numTrialsE.get())
    fileName = fileOpen.cget("text")
    cursorVisible = (clicked.get())   
    itemWidth = int(calibItemE.get())
    if cursorVisible.__eq__('Always Visible'):
        cursor = 1
    if fileCheck == 0 or len(fileName) == 0:
        fileName = 'data.xlsx'
    main(lowerX,upperX, lowerY, upperY, root, subCode,inch, amplitude, targetWidth, fileName, cursor, interT, numT, camera, itemWidth)
    
def width(e):
    x0, y0, x1, y1 = canvas.coords(rectangle) 
    x1 = 2 * float(e)                       
    canvas.coords(rectangle, x0, y0, x1, y1)  
    
def browseFiles():
    filename = filedialog.asksaveasfilename(title = "Create a File", filetypes = (("Excel Files", "*.xlsx*"), ("All files", "*.*")))
    fileOpen.configure(text = filename)
    global fileCheck
    fileCheck = 1
        
hsv = Image.open("hsv.png")
test = hsv.resize((500, 200))
test = ImageTk.PhotoImage(test)
imglabel = Label(image=test)
imglabel.image = test
imglabel.grid(column = 0, columnspan=3, rowspan = 3, padx = (0,30))

lowerX = Label(root, text = "Lower X Bound:")
upperX = Label(root, text = "Upper X Bound:")

lowerY = Label(root, text = "Lower Y Bound:")
upperY = Label(root, text = "Upper Y Bound:")

selected = IntVar()
videoOption1 = Radiobutton(text= 'Camera 1 (Integrated)', value = 0, variable = selected)
videoOption2 = Radiobutton(text= 'Camera 2 (USB)', value = 1, variable = selected)
videoOption3 = Radiobutton(text= 'Camera 3 (USB 2)', value = 2, variable = selected)


example = Label(root, text = "Example for Light Green: LowerX = 50, UpperX = 60  LowerY = 0, UpperY = 150\nTest Camera and Color. After putting color values, pick camera option then hit button.")
example.grid(row = 6, column = 0, rowspan = 2, columnspan = 3)
lowerX.grid(row = 8, column = 0)
upperX.grid(row = 9, column = 0)
lowerY.grid(row = 10, column = 0)
upperY.grid(row = 11, column = 0, pady= (0,10))
lowerXE = Entry(root)
upperXE = Entry(root)
lowerYE = Entry(root)
upperYE = Entry(root)
lowerXE.grid(row = 8, column = 1,)
upperXE.grid(row = 9, column = 1)
lowerYE.grid(row = 10, column = 1,)
upperYE.grid(row =11, column = 1,  pady= (0,10))

videoOption1.grid(row  = 8, column = 2)
videoOption2.grid(row = 9, column = 2)
videoOption3.grid(row = 10, column = 2)
testColor = Button(root, text = "Test Color",command = testCamera)
testColor.grid(row = 11, column = 2)

slider = Scale(root, from_=10 , to=100, orient = HORIZONTAL, bg="white", length = 500,command = width, trough = "black")
slider.grid(row=1, column = 3, columnspan=3)
canvas = Canvas(root,height=50,width=600)
canvas.grid(row = 2, column = 3,  columnspan=3)
info = Label(root, text = "Adust the Slider untill the rectangle measures an INCH in length (use a ruler).\nRemember this number, it will be the same for your computer.")
info.grid(row = 0, column= 3,  columnspan=3)

rectangle =  canvas.create_rectangle(0,50, 25,3*sl_value, fill="black")

warning = Label(root, text ="The sum of Target Width + Amplitude must be less than the screen's width." )
warning.grid(row = 12, column = 0, columnspan = 2)
targwidth = Label(root, text = "Target Width (in): ")
amp = Label(root, text = "Amplitude (in): ")
targwidth.grid(row = 13 , column = 0)
amp.grid(row = 14, column = 0)
twEntry= Entry(root)
ampEntry = Entry(root)
twEntry.grid (row = 13, column = 1)
ampEntry.grid(row = 14, column = 1)


calibItem = Label(root, text = "Item width for camera calibration (in):")
calibItem.grid(row = 15, column = 0, pady = (0,15))
calibItemE = Entry(root)
calibItemE.grid(row = 15, column = 1, pady = (0,15))


interTrial = Label(root, text = "Intertrial Interval (sec): " )
interTrial.grid(row =16, column = 0)
interTrialE = Entry(root)
interTrialE.grid(row = 16, column = 1)

numTrials = Label(root, text = "Number of Trials: ")
numTrials.grid(row = 17, column = 0)
numTrialsE= Entry(root)
numTrialsE.grid(row = 17, column = 1)

pid = Label(root, text = "Subject Code:")
pid.grid(row = 18, column = 0,  pady = (20,20)) 
pidE = Entry(root)
pidE.grid(row = 18, column =1, pady = (20,20))


opCursorL = Label(root, text = "Cursor Visibility:")
optionCursor = ["Always Visible", "Not Visible"]
clicked = StringVar()  
clicked.set( "Always Visible" )
drop = OptionMenu( root , clicked , *optionCursor )
opCursorL.grid(row = 19, column = 0)
drop.grid(row = 19, column = 1)



fileOpen = Label(root, text = "Create File (be sure to add \".xlsx\" at the end):")
fileName = Button(root, text = "Create file",command = browseFiles)
fileOpen.grid(row = 20, column = 0)
fileName.grid(row = 20, column = 1)


submit = Button(root, text ="Submit", command = mainCV)
submit.grid(row =18, column=5)

root.mainloop()