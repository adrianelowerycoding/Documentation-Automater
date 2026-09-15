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
        self.rect_history = []

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
        self.screenshot()

       
    def screenshot(self): 
        bbox = (100, 100, 500, 600)
        screenshot = ImageGrab.grab()
        self.sct_history.append(screenshot)
        #screenshot.save("revert_test.png")

        self.ctk_img = ImageTk.PhotoImage(screenshot)
        self.canvas_image_id = self.canvas.create_image(0,0, anchor="nw", image=self.ctk_img)
        # Reference image copy so it doesn't get garbage collected
        self.canvas.image = self.ctk_img
        self.sct_history.append(self.ctk_img)
        self.update_idletasks()

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
            self.arrow_id = self.canvas.create_line(
                self.start_x, self.start_y, event.x, event.y,
                arrow=tk.LAST,
                arrowshape=(18,22,7),
                width=4,
                fill="red"
            )

    def _on_release(self, event):

        if self.rectangle_is_set:
            end_x = event.x
            end_y = event.y

            # Normalize in case the drag went up/left instead of down/right
            left = min(self.start_x, end_x)
            right = max(self.start_x, end_x)
            top = min(self.start_y, end_y)
            bottom = max(self.start_y, end_y)

            self._capture_region(left, top, right, bottom)
            self.rect_history.append(self.rect_id)

            self.rect_id = None
            # Get screenshot, save the image data and add it to array

        if self.arrow_is_set:

            # put the left, top, right, bottom stuff here?
            self._capture_region(left, top, right, bottom)
            self.current_arrow = None

    def _capture_region(self, left, top, right, bottom):
        # Make sure the canvas/rectangle are fully rendered before we
        # read its screen position -- same reasoning as on_save_btn's
        # update_idletasks() call.
        self.update_idletasks()

        # Canvas's own screen-absolute top-left corner...
        canvas_root_x = self.canvas.winfo_rootx()
        canvas_root_y = self.canvas.winfo_rooty()

        # ...plus the canvas-relative drag coords gives the selection's
        # real on-screen bbox.
        x0 = self.canvas.winfo_rootx()
        y0 = self.canvas.winfo_rooty()
        x1 = x0 + self.canvas.winfo_width()
        y1 = y0 + self.canvas.winfo_height()

        # Guard against a zero-size grab (a click with no real drag)
        if x1 - x0 < 1 or y1 - y0 < 1:
            return

        capture = ImageGrab.grab(bbox=(x0, y0, x1, y1))
        self.sct_history.append(capture)
        capture.save(f"debug_{len(self.sct_history)}.png")
        print(self.sct_history)
        # capture.save(f"capture_{len(self.captures)}.png")

    def revert(self):
        # last index of array - 1 every time revert button is pressed
        # push that to canvas image
        if len(self.sct_history) < 2:
            return
        self.sct_history.pop()
        last_rect_id = self.rect_history.pop()
        self.canvas.delete(last_rect_id) # remove only the most recent rectangle

        self.ctk_img = ImageTk.PhotoImage(self.sct_history[-2])
        self.canvas.itemconfig(self.canvas_image_id, image=self.ctk_img)
        self.update_idletasks()
        print(self.sct_history[-2])

    def set_rectangle(self): 
        self.rectangle_is_set = True

    def set_arrow(self): 
        self.arrow_is_set = True


 


app = ImageWindow()
app.mainloop()