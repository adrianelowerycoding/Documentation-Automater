"""
What this is: 

This is the main side menu that lets you actively format the text your speech transcribes to and take screenshots whenever you
want. When you hit "record" on the home page the main side menu opens up on the right middle of the screen and is instantly 
ready to be used. 

It consists of 2 classes: The MainSideMenu class and the DropdownButton class. The MainSideMenu class is a Top Level that is 
a child of the App class. It holds the frame button_bar which holds the text format and screenshot buttons. It also holds the
side menu toggle button, a mini Top Level that sits right beside the button_bar, which is used to collapse and expand the main
side menu.

The DropdownButton class is a child class of MainSideMenu and is a frame. The DropdownButton frame holds drop down buttons, 
and each drop down button holds a child frame called a dropdown menu. Each drop down menu holds a menu of options associated 
with its drop down button. 

Workflow: 

MainSideMenu determines where on the screen to build its frame, creates its frame, immediately creates its toggle button, then 
begins creating the menu buttons to fill its frame. It pulls the buttons to create from a list of dictionaries defined in its body. 
Depending on the button's type it will either create a regular button or an instance of the DropdownButton class (a drop down button).
A drop down button basically has two commands: 1. The official CTkButton command that's given when the button is created which
creates the drop down menu frame when the button is pressed, and 2. The callback function passed when the instance of DropdownButton
is created, which calls a method from one of the "Options" dictionaries in MainSideMenu. 

"""


import ctypes                  # used to disable DPI scaling awareness
import os                      
import customtkinter as ctk    
import constants                # shared color/style values used across the app
from PIL import Image          

# Force DPI-unaware: Windows will bitmap-scale the window instead of
# letting it react to the real monitor DPI. This avoids the
# Tk scaling-sync bugs by never exposing it to anything other than 100%.
# WARNING: This means the main side menu will stretch to meet the scaled
# % of a display - it won't scale to the display. So the side menu will 
# be much larger on a laptop display than on a PC. 
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(0)  # PROCESS_DPI_UNAWARE
except Exception as e:
    print("shcore failed:", e)


# -- Setting icons path -- 
GUI_DIR = os.path.dirname(os.path.abspath(__file__))
print(GUI_DIR)  
ASSETS_DIR = os.path.join(GUI_DIR, "..","Assets")  

# -- Icon paths -- 
HEADING_ICON_PATH = os.path.join(ASSETS_DIR, "Heading_icon.png")
ITALICS_ICON_PATH = os.path.join(ASSETS_DIR, "Italics_icon.png")
CAMERA_ICON_PATH = os.path.join(ASSETS_DIR, "Camera_icon.png")
BULLET_ICON_PATH = os.path.join(ASSETS_DIR, "bullet_point_icon.png")
ARROW_ICON_PATH = os.path.join(ASSETS_DIR, "arrow_icon.png")

# -- Classes -- 
class MainSideMenu(ctk.CTkToplevel):
    """
    The slide-out formatting toolbar. Owns two windows: `self` (this
    toplevel, holding button_bar) and `self.toggle_win` (a separate tiny
    toplevel with the collapse/expand tab) -- see the comments where
    toggle_win is created for why it has to be a second window rather than
    a widget inside this one.
    """

    def __init__(self, master):
        super().__init__(master)

        # Collapsed = button_bar's whole window hidden, not resized. The
        # toggle button lives in its own separate window (toggle_win below).
        self.collapsed = False
        self.expanded_width = 50
        self.window_height = 500
        self.toggle_width = 20
        self.toggle_height = 50

        self.menu_size_position()      # apply initial width/height/position
        self.update_idletasks()        # force that geometry to take effect immediately
        self.overrideredirect(True)    # remove the OS title bar / window chrome
        self.attributes("-topmost", True)  # keep this window above all others
        self.bind("<Escape>", lambda e: self.destroy())  # Escape closes the menu
        self.after(150, self.menu_size_position)  # re-apply geometry shortly after
                                                   # init, to correct for DPI settling

        # Load and cache each icon once as a CTkImage so button widgets can
        # reference them directly below.
        self.heading_icon = self._load_icon(HEADING_ICON_PATH)
        self.italics_icon = self._load_icon(ITALICS_ICON_PATH)
        self.camera_icon = self._load_icon(CAMERA_ICON_PATH)
        self.bullet_icon = self._load_icon(BULLET_ICON_PATH)
        self.arrow_icon = self._load_icon(ARROW_ICON_PATH)

        # button_bar holds the actual toolbar buttons (heading, italics,
        # bullet, arrow, camera). pack_propagate(False) locks it to the given
        # width/height regardless of what ends up packed/gridded inside it.
        self.button_bar = ctk.CTkFrame(self, width=100, corner_radius=50, fg_color=constants.DARK_FG_COLOR)
        self.button_bar.pack(fill="both", expand=True)
        self.button_bar.pack_propagate(False)
        self.button_bar.grid_columnconfigure(0, weight=1)  # single column, stretches full width

        # toggle_win is a separate CTkToplevel, not placed inside button_bar,
        # so it can't overlap or get buried by button_bar's own buttons.
        # Parented to `self` just to share its Tcl interpreter - withdrawing
        # self does NOT withdraw toggle_win, so the tab stays visible even
        # while button_bar's window is hidden.
        self.toggle_win = ctk.CTkToplevel(self)
        self.toggle_win.overrideredirect(True)     # no title bar on the tab either
        self.toggle_win.attributes("-topmost", True)

        self.toggle_btn = ctk.CTkButton(
            self.toggle_win,
            text="▶",                    # arrow points toward the direction it will expand
            corner_radius=0,
            fg_color=constants.DARK_FG_COLOR,
            command=self.toggle_collapse,
        )
        self.toggle_btn.pack(fill="both", expand=True)  # button fills its whole (tiny) window
        self.position_toggle()          # place it correctly right away
        self.after(150, self.position_toggle)  # ...and again after DPI settles


        # -- Dropdown Buttons Information -- 
        # Naming convention and callback methods for each drop down button. 
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

        # -- Button Creation Information -- 
        # List of dictionaries that hold all needed info for normal and drop down buttons. 
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
            self.button_bar.grid_rowconfigure(row, weight=1, uniform="btn_row")  # equal height per button row

            if entry["type"] == "button": 
                try: 
                    # Plain buttons need a command; build it and place it in this row.
                    self.make_button(entry.get("icon"), entry["command"], "normal", row)
                except KeyError: 
                    # No command was supplied for this entry - skip it rather than crash.
                    print(f"{entry.get("name")} button has no command." )
                    continue
            else: 
                # Dropdown entries get their own self-contained widget
                # instead of a plain button.
                dropdown = DropdownButton( 
                            self.button_bar,
                            icon=entry["icon"],
                            options=entry["options"],
                            callback=on_dropdown_select,  # callback function that happens upon selection/click
                        )
                dropdown.grid(row=row, column=0, sticky="nsew")

            row += 1  # advance to the next grid row

            if i < len(buttons) - 1:
                    # Thin visual separator between buttons - skipped after the last one.
                    divider = ctk.CTkFrame(self.button_bar, height=1, corner_radius=0, fg_color=divider_color)
                    divider.grid(row=row, column=0, sticky="ew")
                    self.button_bar.grid_rowconfigure(row, weight=0)  # dividers don't need to stretch
                    row += 1

    def _load_icon(self, path, size=(20, 20)):
        # Load an image file from disk and wrap it as a CTkImage, so it
        # renders correctly in both light and dark appearance modes.
        img = Image.open(path)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    def menu_size_position(self, window_width=None, window_height=None):
        # Compute and apply this window's size + screen position. Defaults
        # to the expanded width/configured height when not given explicitly,
        # so the no-arg calls above (initial call + DPI-settle call) always
        # size this window back to its normal expanded state.
        if window_width is None:
            window_width = self.expanded_width
        if window_height is None:
            window_height = self.window_height

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = screen_width - window_width           # flush against the right edge of the screen
        y_position = (screen_height - window_height) // 2  # vertically centered
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def position_toggle(self):
        # Sits just left of button_bar when expanded, or flush against the
        # screen edge when collapsed (button_bar's window is withdrawn then).
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        if self.collapsed:
            x_position = screen_width - self.toggle_width
        else:
            x_position = screen_width - self.expanded_width - self.toggle_width  # one toggle-width further left, so it doesn't overlap button_bar
        y_position = (screen_height - self.window_height) // 2 + (self.window_height - self.toggle_height) // 2
        self.toggle_win.geometry(f"{self.toggle_width}x{self.toggle_height}+{x_position}+{y_position}")

    def toggle_collapse(self):
        # Flip collapse state, show/hide button_bar's window, and update
        # the toggle button + its position to match.
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.withdraw()  # hides button_bar's whole window; toggle_win is unaffected
            self.toggle_btn.configure(text="◀")
        else:
            self.deiconify()
            self.toggle_btn.configure(text="▶")
        self.position_toggle()

    def make_button(self, icon, command, state, row):
        # Build one plain (non-dropdown) button_bar button and place it in
        # the given grid row.
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

    # --- Command handlers for button_bar's buttons/dropdown options ---
    # These are placeholders for now - each just prints so wiring can be
    # tested before the real formatting logic can be made. 
    # Kept as separate methods (rather than one shared
    # handler) so each can grow independently later without touching callers.

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
        # Reuse the same state machine the toggle button drives, rather than
        # duplicating its withdraw/flag/reposition steps here. That also means
        # this can never desync self.collapsed from what's actually on screen
        # the way calling self.withdraw() directly (without updating the flag)
        # would.
        self.toggle_collapse()


class DropdownButton(ctk.CTkFrame): # DropdownButton IS a frame; its parent is MainSideMenu
    """
    A self-contained dropdown widget: one CTkButton that shows the
    current selection, plus a hideable frame of option buttons.
    Clicking an option updates the main button's text.
    """

    def __init__(self, parent, icon, options, callback=None, **kwargs):

        # fg_color="transparent" so this wrapper frame has no visible background of its own -
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
        # Opens or closes dropdown_menu 
        if self.menu_open:
            self.close_menu()
        else:
            self.open_menu()


    def open_menu(self):

        # Compute position/size before creating dropdown_menu_frame bc CTkFrame needs
        # width passed into constructor, not place()
        x = self.winfo_x()
        y = self.winfo_y() + self.winfo_height()
        width = self.winfo_width()

        # Build a new frame to hold the option buttons. This frame only exists while the
        # menu is open - it gets destroyed again in close_menu().
        self.dropdown_menu_frame = ctk.CTkFrame(self.master, width=width, fg_color=("gray90", "gray20"))  # light mode, dark mode
        # self.master is button_bar since that's what DropdownButton is parented to

        self.dropdown_menu_frame.place(x=x, y=y)
        self.dropdown_menu_frame.lift()  # make sure it stacks above the other buttons

        # One button per option string, all parented to menu_frame
        for k, v in self.options.items():
            option_btn = ctk.CTkButton(
                self.dropdown_menu_frame,
                text=k,                               # this button's own label is the option text
                fg_color="transparent",               # blends into menu_frame until hovered
                text_color=("black", "white"),        # readable in both appearance modes
                hover_color=("gray80", "gray30"),     
                anchor="w",                           
                # default-arg trick: binds *this* option now, not the last
                # value of the loop variable when the button is later clicked
                command=lambda name=k, cmd=v: self.select_option(name, cmd),
            )
            option_btn.pack(fill="x", padx=2, pady=2)  # stack vertically, full width

        self.menu_open = True  # menu is now visible

    def close_menu(self):
        # Only destroy if a menu_frame actually exists - avoids errors if close_menu()
        if self.dropdown_menu_frame is not None:
            self.dropdown_menu_frame.destroy()  # closes the dropdown menu
            self.dropdown_menu_frame = None     # clear the reference now that it's gone
        self.menu_open = False         # menu is now closed

    def select_option(self, name, command):
        # Called when the user clicks one of the option buttons.
        self.main_button.configure(text=name, image=None)  # updates display of the main drop down button
        self.close_menu()                        # collapse the list now that a choice was made
        if self.callback:                        # calls callback from MainSideMenu "Options" dictionary, IF user provided one
            self.callback(command)

# -- Callback methods -- 
def on_dropdown_select(command):
    # command = the value passed up from DropdownButton.select_option()
    # (this is the dict value for whatever key the user clicked, e.g. self.on_heading_1)
    print("Custom dropdown selection")
    command()