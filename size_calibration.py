from tkinter import *

def grow(line_length):
    line_length.set(line_length.get()+1)

def shrink(line_length):
    line_length.set(line_length.get()-1)

def calibrate_size(my_w):
    print("here")
    line_length = IntVar(master=my_w, value=200)
    
    my_w_child=Toplevel(my_w) # Child window 
    
    window_width = 640 * 2
    window_height = 480 * 2
    my_w_child.geometry(str(window_width)+"x"+str(window_height))  # Size of the window 
    my_w_child.title("Calibrate Test")
    
    up = Button(my_w_child, text ="+", command = lambda: grow(line_length))
    up.pack()
    
    down = Button(my_w_child, text ="-", command = lambda: shrink(line_length))
    down.pack()
    
    myCanvas = Canvas(my_w_child,height=window_height,width=window_width)
    myCanvas.pack()
    
    while True:
        myCanvas.delete(ALL)
            
        print(line_length.get())
        
        # This creates a line of length 200 (straight horizontal line)
        line = myCanvas.create_line(15, 25, line_length.get(), 25)
        
        line = myCanvas.create_line(15, 50, (line_length.get()*2), 50)
        
        my_w_child.update()