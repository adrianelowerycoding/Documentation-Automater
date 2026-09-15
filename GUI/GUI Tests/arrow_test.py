import tkinter as tk

class DragAndCreateSimpleArrow:
    def __init__(self, root):
        self.root = root
        self.root.title("Drag to Create Simple Arrow")
        
        # Create a canvas to draw on
        self.canvas = tk.Canvas(root, width=800, height=600, bg="#f8f9fa")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Track the starting click coordinates and the active object ID
        self.start_x = None
        self.start_y = None
        self.current_arrow = None
        
        # Bind mouse interactions
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        # Store the anchor point where the user first clicks down
        self.start_x = event.x
        self.start_y = event.y
        self.current_arrow = None

    def on_drag(self, event):
        # Delete the previous frame's line so it doesn't leave trailing artifacts
        if self.current_arrow:
            self.canvas.delete(self.current_arrow)
            
        # Draw a line from the original click point to the current mouse position
        # arrow=tk.LAST automatically builds the arrow head at the end point (event.x, event.y)
        # arrowshape defines: (length of cap, length of flare along line, width of flare)
        self.current_arrow = self.canvas.create_line(
            self.start_x, self.start_y, event.x, event.y, 
            arrow=tk.LAST, 
            arrowshape=(18, 22, 7), 
            width=4, 
            fill="#e74c3c"
        )

    def on_release(self, event):
        # Clearing the handle saves the arrow to the canvas permanently
        self.current_arrow = None

if __name__ == "__main__":
    root = tk.Tk()
    app = DragAndCreateSimpleArrow(root)
    root.mainloop()
