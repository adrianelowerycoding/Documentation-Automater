"""
CTk Button Gallery
------------------
A runnable reference showing several CustomTkinter button styles,
including a built-in dropdown (CTkOptionMenu) and a fully custom
dropdown-button combo built from a CTkButton + CTkFrame.

Run directly:  python ctk_button_gallery.py
"""

import customtkinter as ctk  # the CustomTkinter library, aliased to ctk by convention

# Global appearance settings — these apply to every widget created after this point
ctk.set_appearance_mode("System")       # "System" follows the OS, or force "Dark" / "Light"
ctk.set_default_color_theme("blue")     # built-in theme; controls default fg_color etc.


class DropdownButton(ctk.CTkFrame):
    """
    A self-contained dropdown widget: one CTkButton that shows the
    current selection, plus a hideable frame of option buttons.
    Clicking an option updates the main button's text.
    """

    def __init__(self, parent, options, default_text="Select an option", command=None, **kwargs):
        # parent          - the widget this dropdown lives inside (a page frame, the app, etc.)
        # options         - list of strings shown as choices
        # default_text    - text shown on the main button before anything is picked
        # command         - optional function called with the chosen value, e.g. on_dropdown_select
        # **kwargs        - anything else (padx, fg_color, etc.) gets forwarded to CTkFrame

        # fg_color="transparent" so this wrapper frame has no visible background of its own —
        # only the buttons inside it should be visible
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.options = options          # remember the choices so open_menu() can build buttons for them
        self.command = command          # store the optional callback for later use in select_option()
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
        # menu is open — it gets destroyed again in close_menu().
        self.menu_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))  # light mode, dark mode
        self.menu_frame.pack(fill="x", pady=(2, 0))  # sits directly below the main button

        # One button per option string, all parented to menu_frame (not self, not app —
        # this is the "wrong parent" spot to double check if buttons ever show up in the
        # wrong place)
        for option in self.options:
            option_btn = ctk.CTkButton(
                self.menu_frame,
                text=option,                         # this button's own label is the option text
                fg_color="transparent",               # blends into menu_frame until hovered
                text_color=("black", "white"),        # readable in both appearance modes
                hover_color=("gray80", "gray30"),      # visual feedback on mouse-over
                anchor="w",                            # left-align, like a real menu item
                # default-arg trick: binds *this* option now, not the last
                # value of the loop variable when the button is later clicked
                command=lambda opt=option: self.select_option(opt),
            )
            option_btn.pack(fill="x", padx=2, pady=2)  # stack vertically, full width

        self.menu_open = True  # record that the menu is now visible

    def close_menu(self):
        # Only destroy if a menu_frame actually exists — avoids errors if close_menu()
        # is somehow called twice in a row.
        if self.menu_frame is not None:
            self.menu_frame.destroy()  # removes the frame and all its option buttons from the window
            self.menu_frame = None     # clear the reference now that it's gone
        self.menu_open = False         # record that the menu is closed

    def select_option(self, option):
        # Called when the user clicks one of the option buttons.
        self.main_button.configure(text=option)  # this is the actual "update the display button" step
        self.close_menu()                        # collapse the list now that a choice was made
        if self.command:                         # only call it if the caller actually provided one
            self.command(option)


# --- Callback functions -----------------------------------------------------
# Each widget below is wired to one of these via its `command=` parameter.
# CTk calls the function automatically on click/selection; you never call these yourself.

def on_standard_click():
    print("Standard button clicked")


def on_segment_change(value):
    # value = whichever segment label was just selected, e.g. "Week"
    print("Segment selected:", value)


def on_option_menu_change(choice):
    # choice = the string the user picked from the CTkOptionMenu
    print("Option menu selection:", choice)


def on_dropdown_select(choice):
    # choice = the string passed up from DropdownButton.select_option()
    print("Custom dropdown selection:", choice)


# --- Window setup ------------------------------------------------------------

app = ctk.CTk()                          # the root window
app.title("CTk Button Gallery")
app.geometry("360x560")                  # starting width x height in pixels
app.grid_columnconfigure(0, weight=1)    # let column 0 stretch, so widgets can center/fill nicely

# --- Section 1: standard button ----------------------------------------------
ctk.CTkLabel(app, text="Standard button").grid(row=0, column=0, pady=(20, 4))
ctk.CTkButton(app, text="Click Me", command=on_standard_click).grid(row=1, column=0, pady=(0, 20))

# --- Section 2: outline/ghost button, appearance-mode aware -------------------
ctk.CTkLabel(app, text="Outline style, appearance-mode aware").grid(row=2, column=0, pady=(0, 4))
ctk.CTkButton(
    app,
    text="Outline Button",
    fg_color="transparent",                    # no fill, so only the border and text show
    border_width=2,                             # thickness of the outline in pixels
    border_color=("#3B8ED0", "#1F6AA5"),        # (light mode color, dark mode color)
    text_color=("black", "white"),
    hover_color=("gray90", "gray20"),
).grid(row=3, column=0, pady=(0, 20))

# --- Section 3: segmented button (toggle group) --------------------------------
ctk.CTkLabel(app, text="Segmented button (toggle group)").grid(row=4, column=0, pady=(0, 4))
segmented = ctk.CTkSegmentedButton(app, values=["Day", "Week", "Month"], command=on_segment_change)
segmented.set("Week")                    # pre-select a starting value (doesn't fire the command)
segmented.grid(row=5, column=0, pady=(0, 20))

# --- Section 4: built-in dropdown (CTkOptionMenu) -------------------------------
# This widget is both the "main display button" and the dropdown — selecting a
# value rewrites its own text automatically, no extra code required.
ctk.CTkLabel(app, text="Built-in dropdown (CTkOptionMenu)").grid(row=6, column=0, pady=(0, 4))
ctk.CTkOptionMenu(
    app,
    values=["Profile 1", "Profile 2", "Profile 3"],  # the list shown when clicked
    command=on_option_menu_change,                    # fires with the chosen string
).grid(row=7, column=0, pady=(0, 20))

# --- Section 5: custom dropdown-button combo (the DropdownButton class above) ---
ctk.CTkLabel(app, text="Custom dropdown-button combo").grid(row=8, column=0, pady=(0, 4))
custom_dropdown = DropdownButton(
    app,
    options=["Profile A", "Profile B", "Profile C"],
    default_text="Select a profile",
    command=on_dropdown_select,
)
custom_dropdown.grid(row=9, column=0, sticky="ew", padx=40, pady=(0, 20))  # sticky="ew" stretches it

app.mainloop()  # starts the event loop; nothing above this line is actually shown until this runs