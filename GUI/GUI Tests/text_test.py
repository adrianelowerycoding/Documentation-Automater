import tkinter as tk

def start_drag(event):
    # Record the initial mouse position when clicked
    global drag_data
    drag_data = {"x": event.x, "y": event.y}

def drag_text_box(event):
    # Calculate how far the mouse has moved
    delta_x = event.x - drag_data["x"]
    delta_y = event.y - drag_data["y"]
    
    # Move the text box window by that distance
    canvas.move(text_box_window, delta_x, delta_y)
    
    # Update the baseline position for the next movement
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def resize_text_box(event):
    # Get current width and height of the text widget
    current_width = text_widget.winfo_width()
    current_height = text_widget.winfo_height()
    
    # Adjust size based on arrow keys pressed
    if event.keysym == "Right":
        canvas.itemconfigure(text_box_window, width=current_width + 10)
    elif event.keysym == "Left":
        canvas.itemconfigure(text_box_window, width=max(50, current_width - 10))
    elif event.keysym == "Down":
        canvas.itemconfigure(text_box_window, height=current_height + 10)
    elif event.keysym == "Up":
        canvas.itemconfigure(text_box_window, height=max(30, current_height - 10))

# 1. Setup the main window and Canvas
root = tk.Tk()
root.title("Adjustable Text Box on Canvas")

canvas = tk.Canvas(root, width=600, height=400, bg="lightgray")
canvas.pack(fill="both", expand=True)

# 2. Create the standard Text widget
text_widget = tk.Text(root, font=("Helvetica", 12), wrap="word")
# Pre-populate it with some initial text
text_widget.insert("1.0", "Type here...\n\n- Hold left-click on the edge to drag\n- Press arrow keys while typing to resize")

# 3. Embed the Text widget inside the Canvas
text_box_window = canvas.create_window(
    100, 100,           # Initial X, Y coordinates
    window=text_widget, # The widget to embed
    anchor="nw",        # Position relative to top-left corner
    width=250,          # Initial width
    height=150          # Initial height
)

# 4. Add interactive controls
drag_data = {"x": 0, "y": 0}

# Bind dragging to the Canvas (clicking and moving near the text box)
canvas.bind("<Button-1>", start_drag)
canvas.bind("<B1-Motion>", drag_text_box)

# Bind resizing to arrow keys when the text box is focused
text_widget.bind("<KeyPress>", resize_text_box)

root.mainloop()
