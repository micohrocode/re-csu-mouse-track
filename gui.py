from tkinter import *
from version2 import *

# window setup
root = Tk()
root.title('Testing GUI')
root.geometry("640x480")

# function to get slide value
def print_val():
    main(horizontal.get(), horizontal2.get(),root)
    
# get radio button selection
def sel():
   selection = "You selected the option " + str(var.get())
   label.config(text = selection)

# string var to update
var = StringVar()
var.set('hello')

varDub = DoubleVar()
varDub.set(0.00)

# slider
horizontal = Scale(root,from_=85, to=95,resolution=5,orient=HORIZONTAL,digits=3)
horizontal.pack()

# slider
horizontal2 = Scale(root,from_=85, to=95,resolution=5,orient=HORIZONTAL,digits=3)
horizontal2.pack()

submit = Button(root, text ="Submit", command = print_val)
submit.pack()

# label
l = Label(root, textvariable = var)
l.pack()

# text entry
t = Entry(root, textvariable = var)
t.pack()

# int var to update
var = IntVar()
# button 1 
R1 = Radiobutton(root, text="Option 1", variable=var, value=1,
                  command=sel)
R1.pack( anchor = W )
# button 2
R2 = Radiobutton(root, text="Option 2", variable=var, value=2,
                  command=sel)
R2.pack( anchor = W )
# button 3
R3 = Radiobutton(root, text="Option 3", variable=var, value=3,
                  command=sel)
R3.pack( anchor = W)
# radio button selection label
label = Label(root)
label.pack()

root.mainloop()