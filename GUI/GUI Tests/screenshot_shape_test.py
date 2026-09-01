import customtkinter as ctk

class DrawApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CustomTkinter Canvas Drawing")
        self.geometry("600x500")

        # Track tracking/coordinate states
        self.start_x = None
        self.start_y = None
        self.rect_id = None

        # Create CustomTkinter Canvas
        self.canvas = ctk.CTkCanvas(
            self, 
            bg="#2a2a2a", 
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)

        # Bind mouse actions
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        """Record starting coordinates and create initial small rectangle."""
        self.start_x = event.x
        self.start_y = event.y
        
        # Spawn shape with a distinct border and semi-transparent fill look
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="#1f538d",
            width=2,
            fill="#1f538d",
            stipple="gray25"  # Gives a translucent mesh effect
        )

    def on_drag(self, event):
        """Dynamically update rectangle size while mouse moves."""
        if self.rect_id:
            cur_x, cur_y = event.x, event.y
            # Reconfigure existing shape endpoints
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        """Clean reference references so next drag draws a new shape."""
        self.rect_id = None

if __name__ == "__main__":
    app = DrawApp()
    app.mainloop()
