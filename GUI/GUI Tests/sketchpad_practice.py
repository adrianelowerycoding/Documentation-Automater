from  tkinter import * 
from tkinter import ttk

class DrawApp(Canvas): 
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        #self.title("Tkinter Canvas Drawing")
        #self.geometry("600x500")
        self.bind("<Button-1>", self.save)
        self.bind("<B1-Motion>", self.add_line)

    def save(self, event): 
        self.last_x, self.last_y = event.x, event.y

    def add_line(self, event): 
        self.create_line(self.last_x, self.last_y, event.x, event.y)
        self.save(event)




root = Tk() 
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

sketch = DrawApp(root)
sketch.grid(column=0,row=0, sticky=(N,W,E,S))

root.mainloop()
    