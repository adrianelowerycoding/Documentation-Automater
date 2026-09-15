import customtkinter as ctk
from PIL import ImageGrab, ImageTk



class ImageWindow(ctk.CTk): 
    def __init__(self):
        super().__init_()

        self.ctk_img = None
        self.screenshot()

        self.canvas = ctk.CTkCanvas(self, width=800, height=600)
        self.canvas.pack() 
        self.canvas.create_image(0,0, anchor="nw", image=ctk_img)

    

    def screenshot(self): 
        bbox = (100, 100, 100, 100) 
        screenshot = ImageGrab.grab()
        #screenshot.save("revert_test.png")

        ctk_img = ImageTk.PhotoImage(screenshot)
        # Reference image copy so it doesn't get garbage collected
        self.canvas.image = ctk_img

    

root = ctk.CTk()

root.mainloop()