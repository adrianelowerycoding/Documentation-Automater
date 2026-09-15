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
  - Exact-bounds capture: when the image is smaller than the default size,
    the canvas centers it and the leftover space around it is empty gray
    canvas, not part of the image. Screenshotting the canvas's full
    root-coordinate bounds (like before) picks up that gray margin too.
    Fix: remember exactly where _draw_image placed the image (self.image_x/
    self.image_y) and use those + the image's own width/height to build the
    ImageGrab bbox, instead of the canvas's width/height. That grabs only
    the image's actual on-screen footprint, borders excluded, with no need
    to stretch/distort the image to fill the canvas.

"""

import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageGrab
from CTkColorPicker import *


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
        self.button_width = width         # remembered so open_menu() can size the popup to match --
                                           # more reliable than querying winfo_width() at click time

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
    
        # Parent the dropdown menu popup to the whole window, not the toolbar button, so 
        # it won't be constrained to the toolbar button's size/position.
        top_level = self.winfo_toplevel()  # get the top-level window containing this widget
        width = self.button_width
        # x is anchored to the window's right side
        top_level.update_idletasks()  # make sure winfo_width() reflects the real, current size
        x = top_level.winfo_width() - width
        y = self.winfo_rooty() - top_level.winfo_rooty() + self.winfo_height()
        # One row per option, each having the same height.
        height = len(self.options) * self.winfo_height()

        self.dropdown_menu_frame = ctk.CTkFrame(top_level, width=width, height=height, fg_color=("gray90", "gray20"))
        self.dropdown_menu_frame.pack_propagate(False)  # lock to width/height - otherwise it stretches to
                                                         # fit the option buttons' own default size
        self.dropdown_menu_frame.place(x=x, y=y)
        self.dropdown_menu_frame.lift()  # stack it above the toolbar/canvas siblings

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

        # Where _draw_image ends up placing the image's top-left corner,
        # relative to the canvas -- set for real in _draw_image(). Needed
        # later so a "capture the image" action can build a bbox around
        # just the image, not the whole (possibly larger) canvas.
        self.image_x = 0
        self.image_y = 0

        self.title("Edit Menu")
        self._center_on_screen()
        self.resizable(False, False)

        # overrideredirect(True) strips the OS title bar/border. On some
        # platforms the window manager nudges the window's position when
        # those decorations disappear, so the centering math above can be
        # thrown off right after this call. update_idletasks() + a
        # short after() re-apply (same pattern as a real title-bar-less
        # toolbar window) corrects for that once things settle.
        self.update_idletasks()
        self.overrideredirect(True)
        self.after(150, self._center_on_screen)

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

    def _center_on_screen(self):
        # Screen size in pixels, independent of this window's own size.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2

        # Always pass width/height together with the position -- setting
        # only "+x+y" without size can make geometry() fall back to the
        # window's last requested size instead of the one we computed.
        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def _draw_image(self, img):
        self.tk_image = ImageTk.PhotoImage(img)  # keep a reference or it gets garbage collected
        # Center the image within its own area in case that area ended up
        # bigger than the image (i.e. the image was smaller than the
        # default size on that axis). Remember the offset -- this is the
        # top-left corner of the image's actual footprint on the canvas,
        # as opposed to the canvas's own (possibly larger) footprint.
        self.image_x = (self.image_area_width - img.width) // 2
        self.image_y = (self.window_height - img.height) // 2
        self.canvas.create_image(self.image_x, self.image_y, anchor="nw", image=self.tk_image)

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
        self.toolbar.grid_propagate(False)  # fixed size regardless of toolbar_frame's height

        self.toolbar.grid_columnconfigure(0, weight=1)
        for row in range(self.TOOLBAR_BUTTON_COUNT):
            self.toolbar.grid_rowconfigure(row, weight=1, uniform="toolbar_row")
        shape_options = {
            "Option A": self.on_edit_option_a,
            "Option B": self.on_edit_option_b,
        }

        buttons = [
            {"type": "button", "text": "Exit", "command": self.on_exit_btn},
            {"type": "button", "text": "Save", "command": self.on_save_btn},
            {"type": "button", "text": "Color", "command": self.on_color_btn},
            {"type": "dropdown", "text": "Shapes", "options": shape_options},
            {"type": "button", "text": "Revert", "command": self.on_revert_btn},
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
    def on_exit_btn(self):
        print("Button 1 clicked")
        self.destroy()  # close the edit menu window

    def on_save_btn(self):
        print("Button 2 clicked")
        self.update_idletasks()  # ensures the canvas is rendered/positioned first

        # Canvas's own screen-absolute top-left corner...
        canvas_root_x = self.canvas.winfo_rootx()
        canvas_root_y = self.canvas.winfo_rooty()

        # ...plus the offset where the image was actually drawn inside it
        # (self.image_x/self.image_y, set in _draw_image) gives the
        # image's real on-screen top-left corner. Sizing the bbox to the
        # image's own width/height (not the canvas's) means the grab never
        # includes the empty margin around a smaller-than-default image.
        x0 = canvas_root_x + self.image_x
        y0 = canvas_root_y + self.image_y
        x1 = x0 + self.img.width
        y1 = y0 + self.img.height

        self.saved_img = ImageGrab.grab(bbox=(x0, y0, x1, y1))
        self.saved_img.save("screenshot.png")
        self.destroy()  # close the edit menu window



    def on_color_btn(self):
        print("Color button clicked")
    def on_shapes_btn(self):
        print("Shapes button clicked")

    def on_revert_btn(self):
        pass  # TODO

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