"""
This test version exemplifies make the window and frame fit to the size of the image passed 
to it.
"""


import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageGrab

class EditMenu(ctk.CTkToplevel): 
    def __init__(self, master, img): 
        super().__init__(master)

        self.geometry(f"{img.width}x{img.height}")
        self.resizable(False, False) 

        self.image_container = ctk.CTkFrame(self, width=img.width, height=img.height)
        self.image_container.pack(side="top", fill="both", expand=True)
        self.image_container.pack_propagate(False) # Prevent the frame from resizing to fit its content

        self.canvas = tk.Canvas(
            self.image_container, 
            width=img.width, 
            height=img.height,
            highlightthickness=0
            )
        self.canvas.pack(fill="both", expand=True)
        self._draw_image(img) # actually draw the image


    def _draw_image(self, img): 
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0,0, anchor="nw", image=self.tk_image)



if __name__ == "__main__": 
    root = ctk.CTk()
    root.geometry("600x600")

    status_label = ctk.CTkLabel(root, text="Edit Menu Test")
    status_label.pack(pady=(20,10))

    def launch_edit_menu():
        bbox=(100,100,600,500)
        img = ImageGrab.grab(bbox=bbox)
        # img.save("screenshot.png")
        edit_menu = EditMenu(root, img)
        edit_menu.grab_set()  # Make the edit menu modal

    launch_button = ctk.CTkButton(root, text="Launch Edit Menu", command=launch_edit_menu)
    launch_button.pack(pady=(10,20))

    root.mainloop()


