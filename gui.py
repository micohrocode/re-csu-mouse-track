from tkinter import *
from version2 import *

# window setup
root = Tk()
root.title('Testing GUI')
root.geometry("640x480")

# function to get slide value
def print_val():
    x = int(horizontal.get())
    y = int(horizontal2.get())
    main(x,y)

l1 = Label(root, text = "Lower Bound:")
l2 = Label(root, text = "Upper Bound:")
 
l1.grid(row = 0, column = 0, sticky = W, pady = 2)
l2.grid(row = 1, column = 0, sticky = W, pady = 2)
 
horizontal = Entry(root)
horizontal2 = Entry(root)
 

horizontal.grid(row = 0, column = 1, pady = 2)
horizontal2.grid(row = 1, column = 1, pady = 2)
 

submit = Button(root, text ="Submit", command = print_val)
submit.grid(row = 2, column = 1, pady = 2)


root.mainloop()