from tkinter import *
from version2 import *
from PIL import Image, ImageTk



root = Tk()
root.title('Data Acquistion')
sl_value = 10
window_width= root.winfo_screenwidth()               
window_height= root.winfo_screenheight()               
root.geometry("%dx%d" % (window_width,  window_height))

def mainCV():
    lowerX = int(horizontal.get())
    upperX = int(horizontal2.get())
    subCode = pidEntry.get()
    x0, y0, x1, y1 = canvas.coords(rectangle) 
    inch = x1-x0
    targetWidth = float(twEntry.get())
    amplitude = float(ampEntry.get())
    main(lowerX,upperX, root, subCode,inch, amplitude, targetWidth)
    
def width(e):
    x0, y0, x1, y1 = canvas.coords(rectangle) 
    x1 = 2 * float(e)                       
    canvas.coords(rectangle, x0, y0, x1, y1)  
    
hsv = Image.open("hsv.png")
test = hsv.resize((600, 300))
test = ImageTk.PhotoImage(test)
imglabel = Label(image=test)
imglabel.image = test
imglabel.grid(column = 0, columnspan=3, rowspan = 3, padx = (0,30))

l1 = Label(root, text = "Lower X Bound:")
l2 = Label(root, text = "Upper Y Bound:")
l3 = Label(root, text = "Example for Green: Lower = 50, Upper = 60")
l3.grid(row = 6, column = 0)
l1.grid(row = 7, column = 0)
l2.grid(row = 8, column = 0, pady= (0,30))
 
horizontal = Entry(root)
horizontal2 = Entry(root)

horizontal.grid(row = 7, column = 1,)
horizontal2.grid(row = 8, column = 1,  pady= (0,30))
 


slider = Scale(root, from_=10 , to=150, orient = HORIZONTAL, bg="gray", length = 800,command = width)
slider.grid(row=1, column = 4)
canvas = Canvas(root,height=50,width=800)
canvas.grid(row = 2, column = 4)
info = Label(root, text = "Adust the Slider untill the rectangle measures an INCH in length (use a ruler).\nRemember this number, it will be the same for your computer.")
info.grid(row = 0, column= 4)

rectangle =  canvas.create_rectangle(5,50, 25,3*sl_value, fill="black")
targwidth = Label(root, text = "Target Width (in): ")
amp = Label(root, text = "Amplitude (in): ")
targwidth.grid(row = 10, column = 0)
amp.grid(row = 11, column = 0)
twEntry= Entry(root)
ampEntry = Entry(root)
twEntry.grid (row = 10, column = 1)
ampEntry.grid(row = 11, column = 1)


trialDur = Label(root, text = "Intertrial Interval (sec): " )
trialDur.grid(row =12, column = 0)
interTrial = Entry(root)
interTrial.grid(row = 12, column = 1)

calibItem = Label(root, text = "Item width for camera calibration (in):")
calibItem.grid(row = 13, column = 0)
calibItemEntry = Entry(root)
calibItemEntry.grid(row = 13, column = 1)



pid = Label(root, text = "Subject Code:")
pid.grid( row = 14, column = 0,  pady = (20,0)) 
pidEntry = Entry(root)
pidEntry.grid(row = 14, column =1, pady = (20,0))

submit = Button(root, text ="Submit", command = mainCV)
submit.grid(column=5)

root.mainloop()