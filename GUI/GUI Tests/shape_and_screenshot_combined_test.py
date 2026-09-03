
"""
This test uses the body of screenshot_window.py. I'm adding
the functionality of screenshot_shape_test.py, and screenshot_upon_release_test.py

Proposed Changes: 

I don't need the on_click functionality, that was a test for the 
glass window. I want click and drag functionality. I could just 
make a canvas class that fullscreens and combine all the classes
into one class. 

Maybe just replace the glass window with a transparent canvas.
"""

import customtkinter as ctk
import tkinter as tk


class BorderWindow(ctk.CTk):
    """Visual border only. Colorkey middle lets clicks fall through to GlassWindow."""
    def __init__(self, border_color, border_thickness, transparent_color="#abcdef"):
        super().__init__()
        self.attributes("-fullscreen", True)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.config(bg=transparent_color)
        self.wm_attributes("-transparentcolor", transparent_color)

        outer = ctk.CTkFrame(self, fg_color=border_color, corner_radius=0)
        outer.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(outer, fg_color=transparent_color, corner_radius=0)
        inner.pack(fill="both", expand=True, padx=border_thickness, pady=border_thickness)


class GlassWindow(ctk.CTkToplevel):
    """Catches clicks. Sits directly beneath BorderWindow in z-order."""
    def __init__(self, master, on_click=None, alpha=0.02):
        super().__init__(master)
        self.attributes("-fullscreen", True)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", alpha)
        self.configure(fg_color="black")\

    def _handle_click(self, event):
            if self._on_click:
                self._on_click(event.x, event.y)

class GlassCanvas(ctk.CTkToplevel):
    def __init__(self, master, on_click=None):
        super().__init__(master)
        self.attributes("-fullscreen", True)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        transparent_key = "#000001" 
        self.configure(fg_color=transparent_key)
        self.attributes("-transparentcolor", transparent_key)

        self.canvas = tk.Canvas(
            self, 
            highlightthickness=0,
            bg=transparent_key,
        ) 
        self.canvas.pack(fill="both", expand=True)

        # Track tracking/coordinate states
        self.start_x = None
        self.start_y = None
        self.rect_id = None

        # Bind mouse actions 
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event): 
        self.start_x = event.x 
        self.start_y = event.y

        # Spawn shape with a distinct border 
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="#1f538d",
            width=2,
        )

    def on_drag(self, event):
        if self.rect_id:
            cur_x, cur_y = event.x, event.y
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)




class CaptureOverlay:
    """Owns both windows, keeps them stacked correctly, closes them together."""
    def __init__(self, border_color="#FF5733", border_thickness=6, on_click=None):
        self.border_window = BorderWindow(border_color, border_thickness)
        #self.glass_window = GlassWindow(self.border_window, on_click=on_click)

        self.border_window.bind("<Escape>", self.close)
        #self.glass_window.bind("<Escape>", self.close)

        self._keep_border_on_top()

    def _keep_border_on_top(self):
        self.border_window.lift()
        self.border_window.after(50, self._keep_border_on_top)

    def close(self, event=None):
        self.glass_window.destroy()
        self.border_window.destroy()

    def run(self):
        self.border_window.mainloop()


if __name__ == "__main__":
    def handle_click(x, y):
        print(f"clicked at {x}, {y}")

    overlay = CaptureOverlay(on_click=handle_click)
    overlay.run()