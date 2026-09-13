"""

This version sets the top level window at a default size. The default size is 
meant to hold images smaller than the default size and fit to images larger than
the default size. The root window has 3 test buttons that feed a small, medium,
or large image (larger than the default window size) to test how the window and 
the toolbar react to dynamic sizing.

This version combines:
  - Dynamic window/frame sizing based on the image passed in (the image
    area grows to fit the image if the image is bigger than the default
    size, per axis, but never shrinks below the default size).
  - A vertical edit toolbar that lives in its own fixed-width column
    hugging the right side of the window, running the full height of the
    window (top to bottom) so the image can never be drawn underneath it.
    The actual toolbar sits vertically centered within that column in the middle
    right of the window. Only the 3rd button opens a dropdown with 2 options.

"""

import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw


class DropdownButton(ctk.CTkFrame):
    """
    A self-contained dropdown widget for use inside the toolbar: a main
    CTkButton that opens/closes a small popup frame of option buttons
    placed directly below it. Modeled after the DropdownButton pattern
    from the main side menu, trimmed down to text-only buttons.
    """

    def __init__(self, parent, text, options, callback=None, width=120, height=40, **kwargs):
        super().__init__(parent, fg_color="transparent", width=width, height=height, **kwargs)
        self.pack_propagate(False)

        self.options = options            # dict: {option_label: option_command}
        self.callback = callback
        self.dropdown_menu_frame = None
        self.menu_open = False

        self.main_button = ctk.CTkButton(
            self,
            text=text,
            corner_radius=0,
            command=self.toggle_menu,
        )
        self.main_button.pack(fill="both", expand=True)

    def toggle_menu(self):
        if self.menu_open:
            self.close_menu()
        else:
            self.open_menu()

    def open_menu(self):
        # Position/size computed relative to this widget's parent (the
        # toolbar), same approach as the reference DropdownButton.
        x = self.winfo_x()
        y = self.winfo_y() + self.winfo_height()
        width = self.winfo_width()

        self.dropdown_menu_frame = ctk.CTkFrame(self.master, width=width, fg_color=("gray90", "gray20"))
        self.dropdown_menu_frame.place(x=x, y=y)
        self.dropdown_menu_frame.lift()

        for label, command in self.options.items():
            option_btn = ctk.CTkButton(
                self.dropdown_menu_frame,
                text=label,
                fg_color="transparent",
                text_color=("black", "white"),
                hover_color=("gray80", "gray30"),
                anchor="w",
                command=lambda name=label, cmd=command: self.select_option(name, cmd),
            )
            option_btn.pack(fill="x", padx=2, pady=2)

        self.menu_open = True

    def close_menu(self):
        if self.dropdown_menu_frame is not None:
            self.dropdown_menu_frame.destroy()
            self.dropdown_menu_frame = None
        self.menu_open = False

    def select_option(self, name, command):
        self.main_button.configure(text=name)
        self.close_menu()
        if self.callback:
            self.callback(command)


class EditMenu(ctk.CTkToplevel):

    # Default size of the IMAGE AREA only (not counting the toolbar
    # column). This only ever grows - independently per axis - to fit a
    # larger image; it never shrinks below it.
    DEFAULT_IMAGE_WIDTH = 800
    DEFAULT_IMAGE_HEIGHT = 600

    # The toolbar column's fixed footprint. This never changes regardless
    # of how big the window/image is, and is added on top of the image
    # area width - an image can never be drawn underneath it.
    TOOLBAR_WIDTH = 130
    TOOLBAR_BUTTON_HEIGHT = 40
    TOOLBAR_BUTTON_COUNT = 5

    def __init__(self, master, img):
        super().__init__(master)

        self.img = img

        # -- Compute dynamic window size --
        # The image area defaults to DEFAULT_IMAGE_WIDTH x
        # DEFAULT_IMAGE_HEIGHT, growing per-axis to fit the image if it's
        # larger on that axis. The toolbar column's width is then added on
        # top, so the toolbar's space is never eaten into by the image.
        self.image_area_width = max(self.DEFAULT_IMAGE_WIDTH, img.width)
        self.window_height = max(self.DEFAULT_IMAGE_HEIGHT, img.height)
        self.window_width = self.image_area_width + self.TOOLBAR_WIDTH

        self.title("Edit Menu")
        self.geometry(f"{self.window_width}x{self.window_height}")
        self.resizable(False, False)

        # -- Toolbar column (full window height, hugs the right edge) --
        # Built before the image container so the reserved strip exists
        # first; pack order doesn't matter for side="left"/"right" since
        # each claims its own edge regardless of which was packed first.
        self._build_toolbar()

        # -- Image container / canvas (fills whatever's left of the window) --
        self.image_container = ctk.CTkFrame(self, width=self.image_area_width, height=self.window_height)
        self.image_container.pack(side="left", fill="both", expand=True)
        self.image_container.pack_propagate(False)  # frame stays locked to image_area_width/window_height

        self.canvas = tk.Canvas(
            self.image_container,
            width=self.image_area_width,
            height=self.window_height,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self._draw_image(img)

    def _draw_image(self, img):
        self.tk_image = ImageTk.PhotoImage(img)  # keep a reference or it gets garbage collected
        # Center the image within its own area in case that area ended up
        # bigger than the image (i.e. the image was smaller than the
        # default size on that axis).
        x = (self.image_area_width - img.width) // 2
        y = (self.window_height - img.height) // 2
        self.canvas.create_image(x, y, anchor="nw", image=self.tk_image)

    def _build_toolbar(self):
        # toolbar_frame is the permanent, reserved column: full window
        # height, hugging the right edge. Nothing else is ever drawn in
        # this strip, so the image can never end up underneath the
        # toolbar.
        self.toolbar_frame = ctk.CTkFrame(self, width=self.TOOLBAR_WIDTH, corner_radius=0)
        self.toolbar_frame.pack(side="right", fill="y")
        self.toolbar_frame.pack_propagate(False)  # locks the column to TOOLBAR_WIDTH regardless of window height

        toolbar_height = self.TOOLBAR_BUTTON_HEIGHT * self.TOOLBAR_BUTTON_COUNT

        # self.toolbar is the actual button strip, the same width as
        # toolbar_frame, but only tall enough for its 5 buttons. It's
        # placed (not packed) inside toolbar_frame so it can be centered
        # vertically - landing it in the middle-right of the window --
        # while toolbar_frame itself still spans top to bottom.
        self.toolbar = ctk.CTkFrame(self.toolbar_frame, width=self.TOOLBAR_WIDTH, height=toolbar_height, corner_radius=8)
        self.toolbar.place(relx=0.5, rely=0.5, anchor="center")
        self.toolbar.pack_propagate(False)  # fixed size regardless of toolbar_frame's height

        self.toolbar.grid_columnconfigure(0, weight=1)
        for row in range(self.TOOLBAR_BUTTON_COUNT):
            self.toolbar.grid_rowconfigure(row, weight=1, uniform="toolbar_row")

        # Only the 3rd button is a dropdown, with exactly 2 options.
        edit_options = {
            "Option A": self.on_edit_option_a,
            "Option B": self.on_edit_option_b,
        }

        buttons = [
            {"type": "button", "text": "Button 1", "command": self.on_button_1},
            {"type": "button", "text": "Button 2", "command": self.on_button_2},
            {"type": "dropdown", "text": "Edit ▾", "options": edit_options},
            {"type": "button", "text": "Button 4", "command": self.on_button_4},
            {"type": "button", "text": "Button 5", "command": self.on_button_5},
        ]

        for row, entry in enumerate(buttons):
            if entry["type"] == "button":
                btn = ctk.CTkButton(
                    self.toolbar,
                    text=entry["text"],
                    corner_radius=0,
                    command=entry["command"],
                )
                btn.grid(row=row, column=0, sticky="nsew")
            else:
                dropdown = DropdownButton(
                    self.toolbar,
                    text=entry["text"],
                    options=entry["options"],
                    callback=self.on_dropdown_select,
                    width=self.TOOLBAR_WIDTH,
                    height=self.TOOLBAR_BUTTON_HEIGHT,
                )
                dropdown.grid(row=row, column=0, sticky="nsew")

    # -- Placeholder command handlers (print-only, for wiring/testing) --
    def on_button_1(self):
        print("Button 1 clicked")

    def on_button_2(self):
        print("Button 2 clicked")

    def on_button_4(self):
        print("Button 4 clicked")

    def on_button_5(self):
        print("Button 5 clicked")

    def on_edit_option_a(self):
        print("Edit Option A selected")

    def on_edit_option_b(self):
        print("Edit Option B selected")

    def on_dropdown_select(self, command):
        command()


if __name__ == "__main__":

    def make_test_image(width, height, color, label):
        img = Image.new("RGB", (width, height), color)
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), f"{label}\n{width}x{height}", fill="white")
        return img

    root = ctk.CTk()
    root.geometry("420x250")
    root.title("Edit Menu POC")

    status_label = ctk.CTkLabel(root, text="Edit Menu Test - pick an image size")
    status_label.pack(pady=(20, 10))

    def launch_edit_menu(width, height, color, label):
        img = make_test_image(width, height, color, label)
        edit_menu = EditMenu(root, img)
        edit_menu.grab_set()  # modal, matches the reference behavior

    # Default image area is 800x600 (EditMenu.DEFAULT_IMAGE_WIDTH/HEIGHT);
    # the toolbar column's width is added on top of that. Small and medium
    # are both under the default image area, so the image area should stay
    # at the default size in both cases (image centered, toolbar column
    # unaffected). Large exceeds the default on both axes, so the image
    # area - and the window - should grow to match it.
    small_button = ctk.CTkButton(
        root, text="Small Image (400x300)",
        command=lambda: launch_edit_menu(400, 300, "#3B6EA5", "Small"),
    )
    small_button.pack(pady=5)

    medium_button = ctk.CTkButton(
        root, text="Medium Image (700x500)",
        command=lambda: launch_edit_menu(700, 500, "#4E8542", "Medium"),
    )
    medium_button.pack(pady=5)

    large_button = ctk.CTkButton(
        root, text="Large Image (1100x850)",
        command=lambda: launch_edit_menu(1100, 850, "#A5473B", "Large"),
    )
    large_button.pack(pady=5)

    root.mainloop()