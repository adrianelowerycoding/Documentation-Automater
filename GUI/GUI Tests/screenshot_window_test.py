import customtkinter as ctk


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
        self.configure(fg_color="black")

        self._on_click = on_click
        self.bind("<Button-1>", self._handle_click)

    def _handle_click(self, event):
        if self._on_click:
            self._on_click(event.x, event.y)


class CaptureOverlay:
    """Owns both windows, keeps them stacked correctly, closes them together."""
    def __init__(self, border_color="#FF5733", border_thickness=6, on_click=None):
        self.border_window = BorderWindow(border_color, border_thickness)
        self.glass_window = GlassWindow(self.border_window, on_click=on_click)

        self.border_window.bind("<Escape>", self.close)
        self.glass_window.bind("<Escape>", self.close)

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