from tkinter import *
from version2 import *
from PIL import Image, ImageTk



root = Tk()
root.title('Testing GUI')
sl_value = 10
height = win32api.GetSystemMetrics(1)
width = win32api.GetSystemMetrics(0)
root.geometry(str(width) +  "x" + str(height))

def mainCV():
    x = int(horizontal.get())
    y = int(horizontal2.get())
    main(x,y, root, pidEntry.get())

  

def width(e):
    x0, y0, x1, y1 = canvas.coords(rectangle) 
    x1 = 3 * float(e)                       
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
l3.grid(row = 6, column = 1)
l1.grid(row = 7, column = 0)
l2.grid(row = 8, column = 0)
 
horizontal = Entry(root)
horizontal2 = Entry(root)

horizontal.grid(row = 7, column = 1,)
horizontal2.grid(row = 8, column = 1)
 
pid = Label(root, text = "Subject Code:")
pid.grid(row= 9, column = 0,  pady = (0,20)) 
pidEntry = Entry(root)
pidEntry.grid(row=9, column =1, pady = (0,20))

slider = Scale(root, from_=10 , to=150, orient = HORIZONTAL, bg="gray", length = 800,command = width)
slider.grid(row=1, column = 4)
canvas = Canvas(root,height=50,width=800)
canvas.grid(row = 2, column = 4)
info = Label(root, text = "Adust the Slider untill the rectangle measures an INCH in length (use a ruler).\nRemember this number, it will be the same for your computer.")
info.grid(row = 0, column= 4)

rectangle =  canvas.create_rectangle(5,50, 25,3*sl_value, fill="black")


submit = Button(root, text ="Submit", command = mainCV)
submit.grid(column=5)

root.mainloop()