import ctypes
import os
import customtkinter as ctk
import constants
from PIL import Image

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

GUI_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(GUI_DIR, "..", "Assets")
HEADING_ICON_PATH = os.path.join(ASSETS_DIR, "Heading_icon.png")
ITALICS_ICON_PATH = os.path.join(ASSETS_DIR, "Italics_icon.png")
CAMERA_ICON_PATH = os.path.join(ASSETS_DIR, "Camera_icon.png")

class MainSideMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_default_color_theme("blue")
        self.menu_size_position()
        self.update_idletasks()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.bind("<Escape>", lambda e: self.destroy())
        self.after(150, self.menu_size_position)

        # load icons here, not at class-definition time
        self.heading_icon = self._load_icon(HEADING_ICON_PATH)
        self.italics_icon = self._load_icon(ITALICS_ICON_PATH)
        self.camera_icon = self._load_icon(CAMERA_ICON_PATH)

        # button frame
        self.button_bar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=constants.DARK_FG_COLOR)
        self.button_bar.pack(fill="both", expand=True)
        self.button_bar.pack_propagate(False)
        self.button_bar.grid_columnconfigure(0, weight=1)

        buttons = [
            ("", self.heading_icon, self.on_heading, "normal"),
            ("", self.italics_icon, self.on_italics, "normal"),
            ("●", None, self.on_bullet, "normal"),
            (">", None, self.on_arrow, "normal"),
            ("", self.camera_icon, self.on_camera, "normal"),
        ]

        divider_color = "#D3D3D3"  # light gray
        row = 0
        for i, (text, icon, command, state) in enumerate(buttons):
            self.button_bar.grid_rowconfigure(row, weight=1, uniform="btn_row")
            self.make_button(text, icon, command, state, row)
            row += 1

            if i < len(buttons) - 1:
                divider = ctk.CTkFrame(self.button_bar, height=1, corner_radius=0, fg_color=divider_color)
                divider.grid(row=row, column=0, sticky="ew")
                self.button_bar.grid_rowconfigure(row, weight=0)
                row += 1

    def _load_icon(self, path, size=(5, 5)):
        img = Image.open(path)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    def menu_size_position(self, window_width=150, window_height=500):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = screen_width - window_width
        y_position = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def make_button(self, text, icon, command, state, row):
        btn = ctk.CTkButton(
            self.button_bar,
            text=text,
            image=icon,
            font=("Arial", 18),
            corner_radius=0,
            command=command,
            state=state,
            hover=True,
            text_color_disabled="white",
        )
        btn.grid(row=row, column=0, sticky="nsew")
        return btn

    # placeholder commands — wire these up to your real logic
    def on_heading(self):
        print("heading clicked")

    def on_italics(self):
        print("italics clicked")

    def on_bullet(self):
        print("bullet clicked")

    def on_arrow(self):
        print("arrow clicked")

    def on_camera(self):
        print("camera clicked")


if __name__ == "__main__":
    main_side_menu = MainSideMenu()
    main_side_menu.mainloop()