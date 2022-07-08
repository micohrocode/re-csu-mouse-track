from tkinter import *
from version2 import *
from size_calibration import *
from PIL import Image, ImageTk

# window setup
root = Tk()
root.title('Testing GUI')

# height = win32api.GetSystemMetrics(1)
# width = win32api.GetSystemMetrics(0)
# root.geometry(str(width) +  "x" + str(height))
root.geometry("640x480")
# function to get slide value
def print_val():
    x = int(horizontal.get())
    y = int(horizontal2.get())
    partcipantName = pidEntry.get()
    rectWidth = var.get() #1 = thin, #2= medium, #3 = thick
    main(x,y, root, partcipantName, rectWidth)
    
def call_calibrate():
    num = calibrate_size(root)
    print(num)
    
hsv = Image.open("hsv.png")
test = hsv.resize((600, 300))
test = ImageTk.PhotoImage(test)
imglabel = Label(image=test)
imglabel.image = test
imglabel.grid(column = 0, rowspan = 5, columnspan=10)

l1 = Label(root, text = "Lower X Bound:")
l2 = Label(root, text = "Upper Y Bound:")
l3 = Label(root, text = "Example for Red: Lower Bound = 0, Upper Bound = 15")
l3.grid(row = 6, column = 1)
l1.grid(row = 7, column = 0)
l2.grid(row = 8, column = 0)
 
horizontal = Entry(root)
horizontal2 = Entry(root)

horizontal.grid(row = 7, column = 1,)
horizontal2.grid(row = 8, column = 1)
 
pid = Label(root, text = "               Name:")
pid.grid(row= 9, column = 0) 
pidEntry = Entry(root)
pidEntry.grid(row=9, column =1, pady = 5)

TextLabel = Label(root, text = "Pick Rectangle Width")
TextLabel.grid(row= 10, column = 0)

var = IntVar()
R1 = Radiobutton(root, text="Thin", variable=var, value=1)
R1.grid(row = 11, column = 0) 
R2 = Radiobutton(root, text="Medium", variable=var, value=2)
R2.grid(row = 12, column = 0)
R3 = Radiobutton(root, text="Thick", variable=var, value=3)
R3.grid( row = 13, column = 0)

submit = Button(root, text ="Submit", command = print_val)
submit.grid(row = 12, column=1)

calibrate = Button(root, text ="Calibrate", command = call_calibrate)
calibrate.grid(row = 13, column=1)


root.mainloop()