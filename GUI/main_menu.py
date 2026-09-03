import ctypes
import os
import customtkinter as ctk
import constants
from PIL import Image

# Force DPI-unaware: Windows will bitmap-scale our window instead of
# letting it see/react to the real monitor DPI. This avoids the
# CTkImage/Tk scaling-sync bugs entirely by never exposing us to
# anything other than 100%.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(0)  # PROCESS_DPI_UNAWARE
except Exception as e:
    print("shcore failed:", e)


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

        self.heading_icon = self._load_icon(HEADING_ICON_PATH)
        self.italics_icon = self._load_icon(ITALICS_ICON_PATH)
        self.camera_icon = self._load_icon(CAMERA_ICON_PATH)

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

        divider_color = "#D3D3D3"
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

        # --- Dropdown menus attached to the sidebar ---
        # These need to be built here (not at module scope like the original
        # rough draft had them) because they depend on self.button_bar and on
        # bound methods like self.on_heading_1, which only exist once this
        # MainSideMenu instance -- self -- exists. Nothing about what they DO
        # has changed, only where the lines live.
        self.heading_options = {
            "H1": self.on_heading_1,
            "H2": self.on_heading_2,
            "H3": self.on_heading_3,
            "H4": self.on_heading_4,
        }

        self.bullet_options = {}

        self.heading_dropdown = DropdownButton(
            self.button_bar,
            options=self.heading_options,
            default_text="H",
            callback=on_dropdown_select,  # callback function that happens upon selection/click
        )

        self.bullet_dropdown = DropdownButton(
            self.button_bar,
            options=self.bullet_options,
            default_text="●",
            callback=on_dropdown_select,  # callback function that happens upon selection/click
        )

    def _load_icon(self, path, size=(20, 20)):
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
            compound="left",
            font=("Arial", 18),
            corner_radius=0,
            command=command,
            state=state,
            hover=True,
            text_color_disabled="white",
        )
        btn.grid(row=row, column=0, sticky="nsew")
        return btn

    def on_heading(self):
        print("heading clicked")

    def on_heading_1(self):
        print("H1 clicked")

    def on_heading_2(self):
        print("H2 clicked")

    def on_heading_3(self):
        print("H3 clicked")

    def on_heading_4(self):
        print("H4 clicked")

    def on_italics(self):
        print("italics clicked")

    def on_bullet(self):
        print("bullet clicked")

    def on_arrow(self):
        print("arrow clicked")

    def on_camera(self):
        print("camera clicked")


class DropdownButton(ctk.CTkFrame):
    """
    A self-contained dropdown widget: one CTkButton that shows the
    current selection, plus a hideable frame of option buttons.
    Clicking an option updates the main button's text.
    """

    def __init__(self, parent, options, default_text="Select an option", callback=None, **kwargs):
        # parent          - the widget this dropdown lives inside (a page frame, the app, etc.)
        # options         - list of strings shown as choices
        # default_text    - text shown on the main button before anything is picked
        # command         - optional function called with the chosen value, e.g. on_dropdown_select
        # **kwargs        - anything else (padx, fg_color, etc.) gets forwarded to CTkFrame

        # fg_color="transparent" so this wrapper frame has no visible background of its own --
        # only the buttons inside it should be visible
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.options = options          # remember the choices so open_menu() can build buttons for them
        self.callback = callback          # store the optional callback for later use in select_option()
        self.menu_frame = None          # holds the popup frame once it exists; None means "not open"
        self.menu_open = False          # tracks whether the option list is currently visible

        # This is the always-visible button. Its text IS the current selection.
        self.main_button = ctk.CTkButton(
            self,
            text=default_text,          # starts out showing the placeholder text
            command=self.toggle_menu,   # clicking it shows/hides the option list below
            anchor="w",                 # left-align the text instead of centering it
        )
        self.main_button.pack(fill="x")  # stretch to the width of the parent frame

    def toggle_menu(self):
        # Single entry point for the button click: pick open or close based on current state.
        # Equivalent to:
        #     if self.menu_open:
        #         self.close_menu()
        #     else:
        #         self.open_menu()
        self.close_menu() if self.menu_open else self.open_menu()

    def open_menu(self):
        # Build a new frame to hold the option buttons. This frame only exists while the
        # menu is open -- it gets destroyed again in close_menu().
        self.menu_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))  # light mode, dark mode
        self.menu_frame.pack(fill="x", pady=(2, 0))  # sits directly below the main button

        # One button per option string, all parented to menu_frame (not self, not app --
        # this is the "wrong parent" spot to double check if buttons ever show up in the
        # wrong place)
        for k, v in self.options.items():
            option_btn = ctk.CTkButton(
                self.menu_frame,
                text=k,                                # this button's own label is the option text
                fg_color="transparent",               # blends into menu_frame until hovered
                text_color=("black", "white"),        # readable in both appearance modes
                hover_color=("gray80", "gray30"),      # visual feedback on mouse-over
                anchor="w",                            # left-align, like a real menu item
                # default-arg trick: binds *this* option now, not the last
                # value of the loop variable when the button is later clicked
                command=lambda name=k, cmd=v: self.select_option(name, cmd),
            )
            option_btn.pack(fill="x", padx=2, pady=2)  # stack vertically, full width

        self.menu_open = True  # record that the menu is now visible

    def close_menu(self):
        # Only destroy if a menu_frame actually exists -- avoids errors if close_menu()
        # is somehow called twice in a row.
        if self.menu_frame is not None:
            self.menu_frame.destroy()  # removes the frame and all its option buttons from the window
            self.menu_frame = None     # clear the reference now that it's gone
        self.menu_open = False         # record that the menu is closed

    def select_option(self, name, command):
        # Called when the user clicks one of the option buttons.
        self.main_button.configure(text=name)  # this is the actual "update the display button" step
        self.close_menu()                        # collapse the list now that a choice was made
        if self.callback:                         # only call it if the caller actually provided one
            self.callback(command)


def on_dropdown_select(command):
    # command = the value passed up from DropdownButton.select_option()
    # (this is the dict value for whatever key the user clicked, e.g. self.on_heading_1)
    print("Custom dropdown selection")
    command()


if __name__ == "__main__":
    main_side_menu = MainSideMenu()
    main_side_menu.mainloop()