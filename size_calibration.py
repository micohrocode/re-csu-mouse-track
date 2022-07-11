from tkinter import *

sl_value = 10

def width(e):
    # x0, y0, x1, y1 = canvas.coords(rectangle)
    # x1 = 3 * float(e)                      
    # canvas.coords(rectangle, x0, y0, x1, y1)
    pass
   
def calibrate_size(my_w):
    length = IntVar(my_w, 10)
   
    my_w_child=Toplevel(my_w) # Child window 
    window_width = 640 * 2
    window_height = 200 * 2
    my_w_child.geometry(str(window_width)+"x"+str(window_height))  # Size of the window
    canvas = Canvas(my_w_child,height=window_height,width=window_width)
    canvas.pack()
    
    slider = Scale(my_w_child, from_=10 , to=100, orient = HORIZONTAL, bg="blue",command = width, length = 500,variable=length)
    slider.pack(side = BOTTOM)

    my_w_child=Toplevel(my_w) # Child window  
    window_width = 1000
    window_height = 1000
    my_w_child.geometry(str(window_width)+"x"+str(window_height))  # Size of the window
    canvas = Canvas(my_w_child,height=500,width=500)
    canvas.pack()
   
    slider = Scale(my_w_child, from_=10 , to=150, orient = HORIZONTAL, bg="blue", length = 800,variable=length)
    slider.pack()

    submit = Button(my_w_child, text ="Submit")
    submit.pack()
    my_w_child.title("Calibrate Test")

    while True:
        canvas.delete(ALL)
            
        #print(line_length.get())
        print(length.get())
        
        rectangle = canvas.create_rectangle(20,50, 3*length.get(),3*sl_value, fill="green")
        
        rectangle = canvas.create_rectangle(20,50, 3*length.get(),3*sl_value, fill="green")

        my_w_child.update()

    canvas = Canvas(my_w_child,height=window_height,width=window_width)
    canvas.pack()