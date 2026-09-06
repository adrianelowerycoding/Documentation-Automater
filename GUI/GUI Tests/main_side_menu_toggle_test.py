"""
This test is a build on from main_menu_restructure_test. It uses the same structure from that 
test but adds the toggle bar to collapse the button bar. 

"""


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


GUI_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
print(GUI_TEST_DIR)
ASSETS_DIR = os.path.join(GUI_TEST_DIR, "..", "..","Assets")
HEADING_ICON_PATH = os.path.join(ASSETS_DIR, "Heading_icon.png")
ITALICS_ICON_PATH = os.path.join(ASSETS_DIR, "Italics_icon.png")
CAMERA_ICON_PATH = os.path.join(ASSETS_DIR, "Camera_icon.png")
BULLET_ICON_PATH = os.path.join(ASSETS_DIR, "bullet_point_icon.png")
ARROW_ICON_PATH = os.path.join(ASSETS_DIR, "arrow_icon.png")


class MainSideMenu(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        # Collapse now means "is button_bar's whole window hidden," not "is
        # button_bar resized." The toggle lives in its own separate window
        # (see toggle_win below), so collapsing never needs to touch
        # button_bar's size or leave any of its background exposed.
        self.collapsed = False
        self.expanded_width = 50
        self.window_height = 500
        self.toggle_width = 20
        self.toggle_height = 50

        self.menu_size_position()
        self.update_idletasks()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.bind("<Escape>", lambda e: self.destroy())
        self.after(150, self.menu_size_position)

        self.heading_icon = self._load_icon(HEADING_ICON_PATH)
        self.italics_icon = self._load_icon(ITALICS_ICON_PATH)
        self.camera_icon = self._load_icon(CAMERA_ICON_PATH)
        self.bullet_icon = self._load_icon(BULLET_ICON_PATH)
        self.arrow_icon = self._load_icon(ARROW_ICON_PATH)

        self.button_bar = ctk.CTkFrame(self, width=100, corner_radius=50, fg_color=constants.DARK_FG_COLOR)
        self.button_bar.pack(fill="both", expand=True)
        self.button_bar.pack_propagate(False)
        self.button_bar.grid_columnconfigure(0, weight=1)

        # The toggle is its own tiny CTkToplevel, NOT a child of button_bar and
        # NOT overlapping it via place() -- it's a second, independent window
        # sitting right next to this one. That's what stops it from ever being
        # drawn "inside" one of button_bar's grid buttons.
        #
        # It's parented to `self` only so it shares this window's Tcl
        # interpreter -- same reason CTkToplevel is always used instead of a
        # second CTk() root elsewhere in this app. That parenting is just for
        # interpreter bookkeeping though: self.withdraw() does NOT withdraw a
        # child Toplevel, so toggle_win stays visible on its own even while
        # `self` is hidden.
        #
        # Collapsing hides button_bar's ENTIRE window (self.withdraw()) rather
        # than resizing it and hiding just button_bar inside it -- so there's
        # no leftover strip of this window's own background showing next to
        # the toggle button.
        self.toggle_win = ctk.CTkToplevel(self)
        self.toggle_win.overrideredirect(True)
        self.toggle_win.attributes("-topmost", True)

        self.toggle_btn = ctk.CTkButton(
            self.toggle_win,
            text="▶",
            corner_radius=0,
            fg_color=constants.DARK_FG_COLOR,
            command=self.toggle_collapse,
        )
        self.toggle_btn.pack(fill="both", expand=True)
        self.position_toggle()
        self.after(150, self.position_toggle)

        self.heading_options = {
                "H1": self.on_heading_1,
                "H2": self.on_heading_2,
                "H3": self.on_heading_3,
                "H4": self.on_heading_4,
            }
    
        self.bullet_options = {
            "●": self.on_bullet_1,
            "◆": self.on_bullet_2,
            "■": self.on_bullet_3,
        }

        buttons = [
            {"type": "dropdown", "name": "heading", "icon": self.heading_icon, "options": self.heading_options},
            {"type": "button", "name": "italics", "icon": self.italics_icon, "command": self.on_italics},
            {"type": "dropdown", "name": "bullet", "icon": self.bullet_icon, "options": self.bullet_options},
            {"type": "button", "name": "arrow", "icon": self.arrow_icon, "command": self.on_arrow},
            {"type": "button", "name": "camera", "icon": self.camera_icon, "command": self.on_camera}
        ]

        divider_color = "#D3D3D3"
        row = 0
        for i, entry in enumerate(buttons): 
            self.button_bar.grid_rowconfigure(row, weight=1, uniform="btn_row")

            if entry["type"] == "button": 
                try: 
                    self.make_button(entry.get("icon"), entry["command"], "normal", row)
                except KeyError: 
                    print(f"{entry.get("name")} button has no command." )
                    continue
            else: 
                dropdown = DropdownButton( 
                            self.button_bar,
                            icon=entry["icon"],
                            options=entry["options"],
                            callback=on_dropdown_select,  # callback function that happens upon selection/click
                        )
                dropdown.grid(row=row, column=0, sticky="nsew")

            row += 1

            if i < len(buttons) - 1:
                    divider = ctk.CTkFrame(self.button_bar, height=1, corner_radius=0, fg_color=divider_color)
                    divider.grid(row=row, column=0, sticky="ew")
                    self.button_bar.grid_rowconfigure(row, weight=0)
                    row += 1

    def _load_icon(self, path, size=(20, 20)):
        img = Image.open(path)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    def menu_size_position(self, window_width=None, window_height=None):
        if window_width is None:
            window_width = self.expanded_width
        if window_height is None:
            window_height = self.window_height

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = screen_width - window_width
        y_position = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def position_toggle(self):
        # Flush against button_bar's left edge while expanded, or flush
        # against the screen's own right edge while collapsed -- since
        # button_bar's window is fully withdrawn at that point, there's
        # nothing left for the toggle to sit next to.
        #
        # NOTE: "screen_width - expanded_width" alone is button_bar's own left
        # edge, not a position outside it -- placing toggle_win there makes
        # the two windows fully overlap, and self (once deiconified) can then
        # get drawn on top and bury toggle_win entirely. Subtracting
        # toggle_width again pushes toggle_win one more window-width to the
        # left, so it sits just outside button_bar's rectangle instead of
        # inside it.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        if self.collapsed:
            x_position = screen_width - self.toggle_width
        else:
            x_position = screen_width - self.expanded_width - self.toggle_width
        y_position = (screen_height - self.window_height) // 2 + (self.window_height - self.toggle_height) // 2
        self.toggle_win.geometry(f"{self.toggle_width}x{self.toggle_height}+{x_position}+{y_position}")

    def toggle_collapse(self):
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.withdraw()  # hides button_bar's whole window; toggle_win is unaffected
            self.toggle_btn.configure(text="◀")
        else:
            self.deiconify()
            self.toggle_btn.configure(text="▶")
        self.position_toggle()

    def make_button(self, icon, command, state, row):
        btn = ctk.CTkButton(
            self.button_bar,
            text="",
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

    def on_bullet_1(self):
        print("Bullet 1 clicked")

    def on_bullet_2(self):
        print("Bullet 2 clicked")

    def on_bullet_3(self):
        print("Bullet 3 clicked")

    def on_italics(self):
        print("italics clicked")

    def on_bullet(self):
        print("bullet clicked")

    def on_arrow(self):
        print("arrow clicked")

    def on_camera(self):
        print("camera clicked")


class DropdownButton(ctk.CTkFrame): # DropdownButton IS a frame; its parent is MainSideMenu
    """
    A self-contained dropdown widget: one CTkButton that shows the
    current selection, plus a hideable frame of option buttons.
    Clicking an option updates the main button's text.
    """

    def __init__(self, parent, icon, options, callback=None, **kwargs):

        # fg_color="transparent" so this wrapper frame has no visible background of its own --
        # only the buttons inside it should be visible
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.options = options          # remember the dropdown menu choices so open_menu() can build buttons for them
        self.callback = callback          # store the optional callback for later use in select_option()
        self.menu_frame = None          # holds the popup frame once it exists; None means "not open"
        self.menu_open = False          # tracks whether the option list is currently visible

        # This is the always-visible button. Its text IS the current selection.
        self.main_button = ctk.CTkButton(
            self,
            text="",
            text_color="black",
            image=icon,
            command=self.toggle_menu,
            corner_radius=0   # clicking it shows/hides the option list below
        )
        self.main_button.pack(fill="both", expand=True)  # stretch to the width of the parent frame

    def toggle_menu(self):
        # Single entry point for the button click: pick open or close based on current state.
        # Equivalent to:
        #     if self.menu_open:
        #         self.close_menu()
        #     else:
        #         self.open_menu()
        self.close_menu() if self.menu_open else self.open_menu()

    def open_menu(self):

        # Compute position/size before creating dropdown_menu_frame bc CTkFrame needs
        # width passed into constructor, not place()
        x = self.winfo_x()
        y = self.winfo_y() + self.winfo_height()
        width = self.winfo_width()

        # Build a new frame to hold the option buttons. This frame only exists while the
        # menu is open -- it gets destroyed again in close_menu().
        self.dropdown_menu_frame = ctk.CTkFrame(self.master, width=width, fg_color=("gray90", "gray20"))  # light mode, dark mode
        # self.master is button_bar since that's what DropdownButton is parented to

        self.dropdown_menu_frame.place(x=x, y=y)
        self.dropdown_menu_frame.lift()  # make sure it stacks above the other buttons

        # One button per option string, all parented to menu_frame (not self, not app --
        # this is the "wrong parent" spot to double check if buttons ever show up in the
        # wrong place)
        for k, v in self.options.items():
            option_btn = ctk.CTkButton(
                self.dropdown_menu_frame,
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
        if self.dropdown_menu_frame is not None:
            self.dropdown_menu_frame.destroy()  # removes the frame and all its option buttons from the window
            self.dropdown_menu_frame = None     # clear the reference now that it's gone
        self.menu_open = False         # record that the menu is closed

    def select_option(self, name, command):
        # Called when the user clicks one of the option buttons.
        self.main_button.configure(text=name, image=None)  # this is the actual "update the display button" step
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