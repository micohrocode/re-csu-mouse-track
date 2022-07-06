from tkinter import *
from version2 import *
from PIL import Image, ImageTk

# window setup
root = Tk()
root.title('Testing GUI')
root.geometry("640x480")

# function to get slide value
def print_val():
    x = int(horizontal.get())
    y = int(horizontal2.get())
    main(x,y, root, pidEntry.get())

hsv = Image.open("hsv.png")
test = hsv.resize((600, 300))
test = ImageTk.PhotoImage(test)
imglabel = Label(image=test)
imglabel.image = test
imglabel.grid(column = 0, rowspan = 5, columnspan=10)

l1 = Label(root, text = "Lower X Bound:")
l2 = Label(root, text = "Upper Y Bound:")
l1.grid(row = 6, column = 0)
l2.grid(row = 7, column = 0)
 
horizontal = Entry(root)
horizontal2 = Entry(root)
horizontal.grid(row = 6, column = 1,)
horizontal2.grid(row = 7, column = 1)
 
pid = Label(root, text = "               Name:")
pid.grid(row= 9, column = 0)
pidEntry = Entry(root)
pidEntry.grid(row=9, column =1, pady = 5)

submit = Button(root, text ="Submit", command = print_val)
submit.grid(row = 10, column=1)

root.mainloop()