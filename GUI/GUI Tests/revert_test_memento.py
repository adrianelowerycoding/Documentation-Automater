"""
This test is meant to showcase how changes made to a screenshot can be
reverted. This current version uses a memento pattern, which saves a complete
screenshot of the entire state and when you undo a change, it swaps out the 
snapshot of a past time before that change. 

The memento pattern can take up a lot of memory, though. This code already
kind of mixes memento pattern with command pattern, since both the state 
screenshots and the shapes are saved in two different arrays and both 
removed with the "revert" button. I believe switching to only showcasing
the blank initial screenshot and removing the shapes with the "revert" button
will make reversion take up way less memory and simplify the program.

Memento pattern scales badly. Even though in this program the user is rarely going
to be creating hundreds of shapes - and therefore taking hundreds of screenshots - 
learning about how to save memory for users is a crucial lesson and a goal that will
benefit this program as one of the largest goals of this program is to be light-weight.

But that's not to say Command pattern doesn't have its weaknesses also. In larger programs
every distinct command would need its own command class or command id. Luckily in this 
program there are only 2 commands for editing an image: Rectangle and Arrow creation. So this
issue is mute. Command pattern offers immense memory gains and therefore I will choose to use 
it in the next iteration of this test and within my program.

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
        self.sct_history = []
        self.shape_history = []
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
        self.sct_history.append(screenshot) # first item in array is a PIL image
        #screenshot.save("revert_test.png")

        # Converting PIL to PhotoImage and passing it to Canvas
        self.ctk_img = ImageTk.PhotoImage(screenshot)
        self.canvas_image_id = self.canvas.create_image(0,0, anchor="nw", image=self.ctk_img)
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

            self._capture_canvas()
            self.shape_history.append(self.rect_id)

            self.rect_id = None
            # Get screenshot, save the image data and add it to array

        if self.arrow_is_set:

            # put the left, top, right, bottom stuff here?
            self._capture_canvas()
            self.shape_history.append(self.arrow_id)
            self.arrow_id = None

        print(self.shape_history[-1])

    def _capture_canvas(self):
        """This screenshots the canvas."""
        # Make sure the canvas/rectangle are fully rendered before we
        # read its screen position -- same reasoning as on_save_btn's
        # update_idletasks() call.
        self.update_idletasks() # Makes sure the shape pixels are on the canvas before capture

        # ...plus the canvas-relative drag coords gives the selection's
        # real on-screen bbox.
        x0 = self.canvas.winfo_rootx()
        y0 = self.canvas.winfo_rooty()
        x1 = x0 + self.canvas.winfo_width()
        y1 = y0 + self.canvas.winfo_height()

        # Guard against a zero-size grab (a click with no real drag)
        if x1 - x0 < 1 or y1 - y0 < 1:
            return

        # Passing PIL image to sct_history[] array
        capture = ImageGrab.grab(bbox=(x0, y0, x1, y1))
        self.sct_history.append(capture)
        capture.save(f"debug_{len(self.sct_history)}.png")
        print(self.sct_history)
        # capture.save(f"capture_{len(self.captures)}.png")

    def revert(self):

        self.revert_count += 1
        
        match len(self.sct_history): 
            case length if length >= 3: # Shows last pic and removes shape
                self.ctk_img = ImageTk.PhotoImage(self.sct_history[-2])
                self.canvas.itemconfig(self.canvas_image_id, image=self.ctk_img)
                self.sct_history.pop()
                last_shape = self.shape_history.pop()
                self.canvas.delete(last_shape)
                self.update_idletasks()
                print(f"Revert Count: {self.revert_count}")
                print(self.sct_history)
                print(self.shape_history)
            case length if length == 2: #  Just shows blank image and removes shape
                self.ctk_img = ImageTk.PhotoImage(self.sct_history[0])
                self.canvas.itemconfig(self.canvas_image_id, image=self.ctk_img)
                self.sct_history.pop()
                last_shape = self.shape_history.pop()
                self.canvas.delete(last_shape)
                self.update_idletasks()
                print(f"Revert Count: {self.revert_count}")
                print(self.sct_history)
                print(self.shape_history)
            case length if length == 1: # Just shows the blank image; revert button "disabled"
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