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

  - DPI FIX (read this if you're wondering why img.width isn't just used
    directly as a window size anymore): screenshot_window.py runs the whole
    app DPI-unaware, which makes Tkinter think the monitor is smaller than
    it really is. Tkinter's own numbers (geometry(), winfo_rootx(), canvas
    coordinates) all live in that shrunk-down "logical pixel" space. The
    `img` this class receives, though, was captured with ImageGrab in REAL
    "physical pixels" (screenshot_window.py multiplies by the monitor's
    scale factor before grabbing, specifically so the screenshot comes out
    full quality). Those are two different units that happen to be equal
    numbers ONLY when the display is at 100% scaling. This file now takes
    a `dpi_scale` argument so it can convert between the two: physical
    pixels for anything related to the actual captured image data, logical
    pixels for anything related to Tkinter's own window/canvas sizing.

"""

import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageGrab
from CTkColorPicker import *

# Pillow renamed Image.LANCZOS to Image.Resampling.LANCZOS a few versions
# back. This just picks whichever name the installed Pillow actually has,
# so resizing the preview image below doesn't crash on an older/newer
# Pillow than whatever's on your other machine.
try:
    _RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    _RESAMPLE = Image.LANCZOS


class EditMenuGlassWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.attributes("-fullscreen", True)
        self.overrideredirect(True)
        self.attributes("-alpha", 0.02)
        self.attributes("-disabled", True)


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

    def __init__(self, master, img, close_edit_menu_and_glass=None, controller=None, dpi_scale=1.0):
        super().__init__(master)

        # Pass Controller instance from screenshot_window's CaptureOverlay to EditMenu
        self.controller = controller
        # Get screenshot to pass to canvas from screenshot_window's EditPopUp.
        # Keep this around as the full-quality, PHYSICAL-pixel source image —
        # everything we eventually save should trace back to this, not to
        # whatever got drawn on screen.
        self.img = img
        # How many physical pixels there are for every one logical pixel on
        # this monitor (1.0 at 100% scaling, 1.25 at 125%, etc). Comes from
        # CaptureOverlay.dpi_scale in screenshot_window.py, which already
        # did the work of asking Windows for the real number. Defaults to
        # 1.0 so this class still behaves if someone forgets to pass it in
        # (just without the fix — same as before on a 100%-scale screen).
        self.dpi_scale = dpi_scale or 1.0
        self._close_edit_menu_and_glass = close_edit_menu_and_glass
        self.rectangle_is_set = False
        self.arrow_is_set = False
        self.command_history = []

        # -- Compute dynamic window size --
        # The image area defaults to DEFAULT_IMAGE_WIDTH x
        # DEFAULT_IMAGE_HEIGHT, growing per-axis to fit the image if it's
        # larger on that axis. The toolbar column's width is then added on
        # top, so the toolbar's space is never eaten into by the image.
        #
        # DPI FIX: img.width/img.height are PHYSICAL pixels (see the module
        # docstring above), but window_width/window_height feed straight
        # into Tkinter's geometry(), which — because this whole process is
        # DPI-unaware — expects LOGICAL pixels. Using the physical number
        # where Tkinter wants a logical one effectively asks for a window
        # that's `dpi_scale` times too big, and since Windows then stretches
        # an unaware window by `dpi_scale` again when it actually draws it
        # on a scaled screen, the window ends up roughly `dpi_scale` times
        # bigger than intended in every direction. On a scaled laptop
        # display that pushes most of the window off-screen, and all you
        # ever see (or get to save) is the top-left corner that's left on
        # screen — exactly the "zoomed in, cropped" bug. Converting back to
        # logical pixels here, by dividing by dpi_scale, keeps the window
        # the size it's actually supposed to be.
        self.img_logical_width = max(1, round(img.width / self.dpi_scale))
        self.img_logical_height = max(1, round(img.height / self.dpi_scale))

        self.image_area_width = max(self.DEFAULT_IMAGE_WIDTH, self.img_logical_width)
        self.window_height = max(self.DEFAULT_IMAGE_HEIGHT, self.img_logical_height)
        self.window_width = self.image_area_width + self.TOOLBAR_WIDTH

        # Where _draw_image ends up placing the image's top-left corner,
        # relative to the canvas -- set for real in _draw_image(). Needed
        # later so a "capture the image" action can build a bbox around
        # just the image, not the whole (possibly larger) canvas. This is
        # in the same logical-pixel space as everything else Tkinter works
        # with here.
        self.image_x = 0
        self.image_y = 0

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

        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.shape_color = "red"

        # Bind mouse events
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

    # -- Window and Toolbar creation methods --
    def _center_on_screen(self):
        # Screen size in pixels, independent of this window's own size.
        # winfo_screenwidth/height() also report the LOGICAL screen size
        # (same DPI-unaware space window_width/window_height are now in
        # above), so this comparison stays apples-to-apples.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2

        # Always pass width/height together with the position -- setting
        # only "+x+y" without size can make geometry() fall back to the
        # window's last requested size instead of the one we computed.
        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def _draw_image(self, img):
        # DPI FIX: img is still full-resolution (physical pixels). If we
        # handed that straight to ImageTk.PhotoImage and drew it onto a
        # canvas that's sized in logical pixels, the picture would be
        # `dpi_scale` times bigger than the canvas meant to hold it — same
        # flavor of bug as the window sizing above, just for the image
        # itself instead of the whole window.
        #
        # The trick: shrink the image down to the LOGICAL size for display
        # only. Because this window is DPI-unaware, Windows takes whatever
        # we draw at that logical size and stretches it back up by
        # dpi_scale when it actually paints the screen — so a logical-size
        # image ends up looking full-size again once it's on the monitor.
        # self.img (the original, full-res PIL Image) is left untouched, so
        # nothing here throws away any quality for the final saved file.
        if self.dpi_scale != 1:
            display_img = img.resize(
                (self.img_logical_width, self.img_logical_height), _RESAMPLE
            )
        else:
            # At 100% scaling physical and logical pixels are the same
            # number, so there's nothing to convert — skip the resize
            # entirely rather than pay for a no-op resample.
            display_img = img

        self.tk_image = ImageTk.PhotoImage(display_img)  # keep a reference or it gets garbage collected
        # Center the image within its own area in case that area ended up
        # bigger than the image (i.e. the image was smaller than the
        # default size on that axis). Remember the offset -- this is the
        # top-left corner of the image's actual footprint on the canvas,
        # as opposed to the canvas's own (possibly larger) footprint. This
        # is in logical pixels, matching display_img's (logical) size.
        self.image_x = (self.image_area_width - display_img.width) // 2
        self.image_y = (self.window_height - display_img.height) // 2
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
            "Rectangle": self.set_rectangle,
            "Arrow": self.set_arrow,
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

    # -- Drawing methods --

    def _on_press(self, event):
        if self.rectangle_is_set:
            self.start_x = event.x
            self.start_y = event.y

            # Create a temporary rectangle w/ no thickness yet
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline=self.shape_color, width=2
            )
        else:
            self.start_x = event.x
            self.start_y = event.y
            self.arrow_id = None

    def _on_drag(self, event):
        if self.rectangle_is_set:
            cur_x, cur_y = event.x, event.y
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)
        else:
             # Delete the previous frame's line so it doesn't leave trailing artifacts
            if self.arrow_id:
                self.canvas.delete(self.arrow_id)

            # Draw a line from the original click point to the current mouse position
            self.arrow_id = self.canvas.create_line(
                self.start_x, self.start_y, event.x, event.y,
                arrow=tk.LAST,
                arrowshape=(18,22,7),
                width=4,
                fill=self.shape_color
            )

    def _on_release(self, event):

        if self.rectangle_is_set:

            self.update_idletasks()
            self.command_history.append(self.rect_id)

            self.rect_id = None
            # Get screenshot, save the image data and add it to array

        if self.arrow_is_set:

            # put the left, top, right, bottom stuff here?
            self.update_idletasks()
            self.command_history.append(self.arrow_id)
            self.arrow_id = None

        print(self.command_history)

    # -- Toolbar Commands --
    def on_exit_btn(self):
        print("Button 1 clicked")
        # Destroy EditMenu and EditMenuGlass
        if self._close_edit_menu_and_glass:
            self._close_edit_menu_and_glass()

    def on_save_btn(self):
        print("Button 2 clicked")
        self.update_idletasks()  # ensures the canvas is rendered/positioned first

        # Canvas's own screen-absolute top-left corner...
        canvas_root_x = self.canvas.winfo_rootx()
        canvas_root_y = self.canvas.winfo_rooty()

        # ...plus the offset where the image was actually drawn inside it
        # (self.image_x/self.image_y, set in _draw_image) gives the
        # image's real on-screen top-left corner. Both of those numbers are
        # LOGICAL pixels — winfo_rootx/rooty() are Tkinter numbers, and
        # we're in a DPI-unaware process, so that's the space they live in.
        #
        # DPI FIX: ImageGrab.grab() always wants PHYSICAL pixel
        # coordinates, no matter how the process declared its own DPI
        # awareness (that's exactly why screenshot_window.py multiplies by
        # dpi_scale before its own ImageGrab call). Previously this method
        # added self.img.width/height — a PHYSICAL pixel count — straight
        # onto a LOGICAL-pixel origin, which mismatched units and produced
        # a bbox that didn't line up with anything real on screen. The fix
        # converts the origin up to physical pixels first (multiply by
        # dpi_scale), then adds the physical width/height on top of that —
        # now everything going into the bbox is physical pixels, same as
        # the original capture in screenshot_window.py.
        s = self.dpi_scale
        x0 = round((canvas_root_x + self.image_x) * s)
        y0 = round((canvas_root_y + self.image_y) * s)
        x1 = x0 + self.img.width
        y1 = y0 + self.img.height

        self.saved_img = ImageGrab.grab(bbox=(x0, y0, x1, y1))
        self.controller.sct_save(self.saved_img)
        # self.saved_img.save("screenshot.png")

        # Destroy Edit Menu and EditMenuGlass
        if self._close_edit_menu_and_glass:
            self._close_edit_menu_and_glass()

    def on_color_btn(self):
        print("Color button clicked")

        pick_color = AskColor()
        pick_color.attributes("-topmost", True)
        pick_color.lift(self)
        pick_color.focus_force()
        color = pick_color.get()

        if color:
            self.shape_color = color
            print(f"Selected color: {self.shape_color}")


    def on_shapes_btn(self):
        print("Shapes button clicked")

    def on_revert_btn(self):
        #self.revert_count += 1

        # Revert btn pressed -> Pops last index from
        # command_history[]
        match len(self.command_history):
            case length if length != 0:
                last_command = self.command_history.pop()
                self.canvas.delete(last_command)
                self.update_idletasks()
                #print(f"Revert Count: {self.revert_count}")
                print(self.command_history)
            case length if length == 0:
                #self.revert_count = 0
                pass

    def set_rectangle(self):
        self.rectangle_is_set = True
        self.arrow_is_set = False

    def set_arrow(self):
        self.arrow_is_set = True
        self.rectangle_is_set = False

    def on_dropdown_select(self, command):
        command()