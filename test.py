from tkinter import *

global s, s1, s2, s3
sl_value = 10
def width(e):
    x0, y0, x1, y1 = canvas.coords(rectangle) # get the coords of rect
    x1 = 3 * float(e)                         # calc new coords
    canvas.coords(rectangle, x0, y0, x1, y1)  # set new coords
   
   
def testr():
  global x, y, x2, y2
  x, y, x2, y2 =  canvas.coords(rectangle)
  print("CHECK:", canvas.coords(rectangle))

  diff = x2-x
 
 
  rect2=  canvas.create_rectangle(x,y+50,x + (diff*2), y2+50, fill="black")
  print("CHECK2:", canvas.coords(rect2))

 
root = Tk()
frame = Frame(root)
frame.pack()

slider = Scale(frame, from_=10 , to=100, orient = HORIZONTAL, bg="blue",command = width)
slider.pack()
canvas = Canvas(root,height=500,width=360)
canvas.pack()
rectangle = canvas.create_rectangle(20,50, 40,3*sl_value, fill="green")

submit = Button(root, text ="Submit", command = testr)

submit.pack()


root.mainloop()