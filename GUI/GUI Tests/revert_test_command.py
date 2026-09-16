"""
This is a test of reversion with the command pattern. It's way simpler and 
uses way less memory than the memento pattern. It simply uses the id of the
shape created and uses that id to delete the shape from the canvas.
"""

import customtkinter as ctk
import tkinter as tk
from PIL import ImageGrab, ImageTk



class ImageWindow(ctk.CTk): 
    def __init__(self):
        super().__init__()

        self.revert_button = ctk.CTkButton(
            self,
            text="Revert",
            command=self.revert
        )
        self.revert_button.pack(pady=10)

        self.rectangle_button = ctk.CTkButton(
           self,
           text="Rect",
           command=self.set_rectangle
        )
        self.rectangle_button.pack(pady=10)

        self.arrow_button = ctk.CTkButton(
            self,
            text="Arrow",
            command=self.set_arrow
        )
        self.arrow_button.pack(pady=10)

        self.rectangle_is_set = False
        self.arrow_is_set = False
        self.command_history = []
        self.revert_count = 0

        self.canvas = tk.Canvas(self, width=800, height=600)
        self.canvas.pack()
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.arrow_id = None

        # Bind mouse events
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        self.ctk_img = None
        self.initial_screenshot()

       
    def initial_screenshot(self): 

        # Starting image
        screenshot = ImageGrab.grab()

        # Converting PIL to PhotoImage and passing it to Canvas
        self.ctk_img = ImageTk.PhotoImage(screenshot)
        self.canvas.create_image(0,0, anchor="nw", image=self.ctk_img)
        # Reference image copy so it doesn't get garbage collected
        self.canvas.image = self.ctk_img
        self.update_idletasks() # Updating canvas to show image

    def _on_press(self, event):
        if self.rectangle_is_set:
            self.start_x = event.x
            self.start_y = event.y

            # Create a temporary rectangle w/ no thickness yet
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline="red", width=4
            )
        else: 
            self.start_x = event.x
            self.start_y = event.y
            self.arrow_id = None

    def _on_drag(self, event): 
        if self.rectangle_is_set:
            cur_x, cur_y = event.x, event.y
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)

        else: 
            # Delete the previous frame's line so it doesn't leave trailing artifacts
            if self.arrow_id: 
                self.canvas.delete(self.arrow_id)

            # Draw a line from the original click point to the current mouse position
            self.arrow_id = self.canvas.create_line(
                self.start_x, self.start_y, event.x, event.y,
                arrow=tk.LAST,
                arrowshape=(18,22,7),
                width=4,
                fill="red"
            )

    def _on_release(self, event):

        if self.rectangle_is_set:

            self.update_idletasks()
            self.command_history.append(self.rect_id)

            self.rect_id = None
            # Get screenshot, save the image data and add it to array

        if self.arrow_is_set:

            # put the left, top, right, bottom stuff here?
            self.update_idletasks()
            self.command_history.append(self.arrow_id)
            self.arrow_id = None

        print(self.command_history)

    def revert(self):

        self.revert_count += 1

        # Revert btn pressed -> Pops last index from 
        # command_history[]
        match len(self.command_history):
            case length if length != 0: 
                last_command = self.command_history.pop()
                self.canvas.delete(last_command)
                self.update_idletasks()
                print(f"Revert Count: {self.revert_count}")
                print(self.command_history)
            case length if length == 0: 
                self.revert_count = 0
                pass
        
    def set_rectangle(self): 
        self.rectangle_is_set = True
        self.arrow_is_set = False

    def set_arrow(self): 
        self.arrow_is_set = True
        self.rectangle_is_set = False


 


app = ImageWindow()
app.mainloop()