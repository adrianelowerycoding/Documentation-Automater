

import customtkinter as ctk
import tkinter as tk
from PIL import ImageGrab
import ctypes

# Load the two Windows DLLs used to detect the real display scale factor
_user32 = ctypes.windll.user32
_gdi32 = ctypes.windll.gdi32
_user32.GetDC.restype = ctypes.c_void_p          # must set restype or the
_user32.GetDC.argtypes = [ctypes.c_void_p]       # HDC gets truncated to
_user32.ReleaseDC.argtypes = [ctypes.c_void_p, ctypes.c_void_p]  # 32 bits
_gdi32.GetDeviceCaps.argtypes = [ctypes.c_void_p, ctypes.c_int]  # on 64-bit

HORZRES = 8            # GetDeviceCaps code: logical (scaled-down) width
DESKTOPHORZRES = 118   # GetDeviceCaps code: true physical width

# Remove DPI Awareness so scaling issue is fixed; will stretch windows on scaled monitors
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(0)  # PROCESS_DPI_UNAWARE
except Exception as e:
    print("shcore failed:", e)

def get_dpi_scale():
    """Physical pixels per logical pixel, e.g. 1.25 at 125% scaling.
    DESKTOPHORZRES always reports true physical width; HORZRES follows
    whatever DPI virtualization applies to the calling process — so their
    ratio is the scale factor, independent of this process's own awareness."""
    hdc = _user32.GetDC(None)  # device context for the whole screen
    try:
        return _gdi32.GetDeviceCaps(hdc, DESKTOPHORZRES) / _gdi32.GetDeviceCaps(hdc, HORZRES)  # physical ÷ logical = scale
    finally:
        _user32.ReleaseDC(None, hdc)  # always free the DC, even on error

class BorderWindow(ctk.CTkToplevel):
    """Visual border only. Colorkey middle lets clicks fall through to GlassWindow.

    This is the persistant visual cue that you are in "screenshot mode". It's always visible.
    """
    def __init__(self, master, border_color, border_thickness, transparent_color="#abcdef"):
        super().__init__(master)
        self.attributes("-fullscreen", True)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.config(bg=transparent_color)
        self.wm_attributes("-transparentcolor", transparent_color)

        outer = ctk.CTkFrame(self, fg_color=border_color, corner_radius=0)
        outer.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(outer, fg_color=transparent_color, corner_radius=0)
        inner.pack(fill="both", expand=True, padx=border_thickness, pady=border_thickness)


class SelectionBox(ctk.CTkToplevel):
    """
    Purely cosmetic drag-rectangle indicator. Fully opaque border (so it's
    visible over GlassWindow's near-invisible alpha), colorkeyed interior
    (so the area inside the rectangle stays see-through to the real
    desktop). Resized on every drag update instead of staying fullscreen.

    Never binds mouse events on purpose — see module docstring for why
    that's safe.

    Has to have the border because if not it would just be a see-through, click-through
    window and wouldn't be focused at all.

    This window only exists when you're actively dragging a selection. It's hidden until button
    press and only shows the specific rectangle you're drawing.
    """
    def __init__(self, master, color="red", thickness=2):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self._key = "#123456"
        self.wm_attributes("-transparentcolor", self._key)
        self.configure(fg_color=self._key)
        self.thickness = thickness

        outer = ctk.CTkFrame(self, fg_color=color, corner_radius=0)
        outer.pack(fill="both", expand=True)
        inner = ctk.CTkFrame(outer, fg_color=self._key, corner_radius=0)
        inner.pack(fill="both", expand=True, padx=thickness, pady=thickness)

        self.withdraw()  # hidden until a drag actually starts

    def show_at(self, x1, y1, x2, y2):
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))
        # Enforce a minimum so the colorkeyed inner frame never has to be
        # packed into a negative/zero-size window (Tk will error on that).
        w = max(x2 - x1, self.thickness * 2 + 1)
        h = max(y2 - y1, self.thickness * 2 + 1)
        self.geometry(f"{w}x{h}+{x1}+{y1}")
        self.deiconify()

    def hide(self):
        self.withdraw()


class GlassWindow(ctk.CTkToplevel):
    """
    See-through (alpha) AND clickable. Sits directly beneath BorderWindow's
    colorkey hole in z-order. Handles all drag events and reports
    screen-absolute coordinates via callbacks; draws nothing itself.

    Alpha windows stay fully hit-testable in Tk/Windows — that's the
    property this class depends on. Don't add transparentcolor here; it
    would make this window click-through too, and clicks would reach the
    real desktop instead of this window.
    """
    def __init__(self, master, on_press=None, on_drag=None, on_release=None, alpha=0.02):
        super().__init__(master)
        self.attributes("-fullscreen", True)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", alpha)
        self.configure(fg_color="black")

        self._on_press = on_press
        self._on_drag = on_drag
        self._on_release = on_release

        # A plain tk.Canvas as the actual event target — customtkinter
        # widgets can layer internal elements over the toplevel, so binding
        # on an explicit child widget is more reliable than binding on the
        # toplevel itself.
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="black")
        self.canvas.pack(fill="both", expand=True)

        # Event listeners
        self.canvas.bind("<Button-1>", self._handle_press)
        self.canvas.bind("<B1-Motion>", self._handle_drag)
        self.canvas.bind("<ButtonRelease-1>", self._handle_release)

    def _handle_press(self, event):
        if self._on_press:
            self._on_press(event.x_root, event.y_root)

    def _handle_drag(self, event):
        if self._on_drag:
            self._on_drag(event.x_root, event.y_root)

    def _handle_release(self, event):
        if self._on_release:
            self._on_release(event.x_root, event.y_root)


class EditPopUp(ctk.CTkToplevel):
    """After screenshot button release this window pops up asking user if they want to
    save or edit current screenshot.

    Stays hidden (withdrawn) from the moment it's created until
    CaptureOverlay explicitly calls show_at() — that's what makes it only
    appear on release instead of the instant the overlay launches.
    """

    WIDTH = 300
    HEIGHT = 50

    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.screenshot = None  # will be set on release

        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        save_btn = ctk.CTkButton(self, text="Save", fg_color="blue", command=self.save_screenshot)
        save_btn.pack(side="left")

        edit_btn = ctk.CTkButton(self, text="Edit", fg_color="blue")
        edit_btn.pack(side="right")

        self.withdraw()  # hidden until a valid selection is released

    def show_at(self, x, y):
        # Clamp so the popup doesn't get placed off-screen when the
        # selection ends near a screen edge.
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = min(max(x, 0), max(screen_w - self.WIDTH, 0))
        y = min(max(y, 0), max(screen_h - self.HEIGHT, 0))

        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")
        self.deiconify()
        self.lift()

    def hide(self):
        self.withdraw()

    def set_screenshot(self, screenshot):
        self.screenshot = screenshot

    def save_screenshot(self):
        if self.screenshot is not None:
            self.screenshot.save("screenshot.png")
            print("Saved screenshot.png")

    def on_edit(self): 
        # Has to pass screenshot to edit_menu and 
        # open edit_menu
        pass



class CloseButtonWindow(ctk.CTkToplevel):
    """
    The red "X" close control: a plain square red box with a white "x",
    docked flush against the right edge of the screen. Its own Toplevel —
    not a widget inside BorderWindow — so it can be withdrawn independently
    of the border/hole/glass stack.

    This is the collapsible half of a dock/toggle pair: CloseToggleTab is
    the always-visible half that brings it back.
    """

    WIDTH = 40
    HEIGHT = 40
    Y = 20  # fixed distance from the top of the screen

    def __init__(self, master, on_close, on_press=None, on_release=None):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.close_btn = ctk.CTkButton(
            self,
            text="✕",
            width=self.WIDTH,
            height=self.HEIGHT,
            corner_radius=0,          # plain box, not a circle
            fg_color="red",
            hover_color="#b30000",
            text_color="white",
            command=on_close,
        )
        self.close_btn.pack(fill="both", expand=True)

        # add="+" so these run alongside the button's own press/release
        # handling instead of replacing it — see CaptureOverlay.
        # _pause_stacking/_resume_stacking for why this exists.
        if on_press is not None:
            self.close_btn.bind("<ButtonPress-1>", on_press, add="+")
        if on_release is not None:
            self.close_btn.bind("<ButtonRelease-1>", on_release, add="+")

        self.position()

    def position(self):
        # Flush against the right edge — the same screen_width - window_width
        # pattern MainSideMenu.menu_size_position uses to dock button_bar.
        screen_width = self.winfo_screenwidth()
        x = screen_width - self.WIDTH
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{self.Y}")


class CloseToggleTab(ctk.CTkToplevel):
    """
    Small always-visible tab beside CloseButtonWindow. Clicking it collapses
    (withdraws) or expands (deiconifies) CloseButtonWindow — the same
    collapsed/expanded split MainSideMenu.toggle_win drives for button_bar,
    just with one button standing in for the whole toolbar.
    """

    WIDTH = 16
    HEIGHT = CloseButtonWindow.HEIGHT

    def __init__(self, master, on_toggle, on_press=None, on_release=None):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.collapsed = False

        self.toggle_btn = ctk.CTkButton(
            self,
            text="▶",  # points toward the direction CloseButtonWindow expands from
            corner_radius=0,
            fg_color="#2b2b2b",       # dark neutral, not red — this is a
            hover_color="#3d3d3d",    # navigation control, not a warning
            text_color="white",
            command=on_toggle,
        )
        self.toggle_btn.pack(fill="both", expand=True)

        if on_press is not None:
            self.toggle_btn.bind("<ButtonPress-1>", on_press, add="+")
        if on_release is not None:
            self.toggle_btn.bind("<ButtonRelease-1>", on_release, add="+")

        self.position()

    def position(self):
        screen_width = self.winfo_screenwidth()
        if self.collapsed:
            x = screen_width - self.WIDTH
        else:
            x = screen_width - CloseButtonWindow.WIDTH - self.WIDTH
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{CloseButtonWindow.Y}")

    def set_collapsed(self, collapsed):
        self.collapsed = collapsed
        self.toggle_btn.configure(text="◀" if collapsed else "▶")
        self.position()
        self.update_idletasks()  # flush the new geometry immediately, so the
                                  # tab visibly snaps flush to the edge the
                                  # instant the X is retracted, not on the
                                  # next idle cycle


class CaptureOverlay:
    """Owns all six windows, keeps them stacked correctly, closes them together."""
    def __init__(self, master, border_color="#FF5733", border_thickness=6):
        self.border_window = BorderWindow(master, border_color, border_thickness)
        self.selection_box = SelectionBox(master, color="red", thickness=2)
        self.glass_window = GlassWindow(
            master,
            on_press=self._on_press,
            on_drag=self._on_drag,
            on_release=self._on_release,
        )
        self.dpi_scale = get_dpi_scale()  # scale factor to fix screenshot cropping (see get_dpi_scale)
        self.pop_up = EditPopUp(master)

        # Red "X" close control, docked to the right edge of the screen and
        # retractable via its own toggle tab. Both get pause/resume hooks
        # into the periodic re-lift below, so a click on either of them
        # never races against it.
        self.close_button = CloseButtonWindow(
            master, on_close=self.close,
            on_press=self._pause_stacking, on_release=self._resume_stacking,
        )
        self.close_toggle = CloseToggleTab(
            master, on_toggle=self.toggle_close_button,
            on_press=self._pause_stacking, on_release=self._resume_stacking,
        )

        self.start_x = self.start_y = 0

        self.border_window.bind("<Escape>", self.close)
        self.glass_window.bind("<Escape>", self.close)

        self._stack_job = None
        self._keep_border_on_top()

    def _keep_border_on_top(self):
        # Matches the original known-working pattern: BorderWindow needs
        # periodic re-lifting to counter the OS/WM occasionally reshuffling
        # -topmost windows (most commonly triggered by clicking/dragging on
        # GlassWindow itself, which Windows tends to raise on click).
        # close_button/close_toggle ride along in the same cycle so they
        # stay above border_window too — see the module docstring for why
        # clicks on THEM pause this loop instead of fighting it.
        self.border_window.lift()
        if not self.close_toggle.collapsed:
            # Don't lift a withdrawn window — it has nothing to do with
            # z-order while hidden, and skipping it here removes any risk
            # of a stray lift() nudging it back into view while retracted.
            self.close_button.lift()
        self.close_toggle.lift()
        self._stack_job = self.border_window.after(50, self._keep_border_on_top)

    def _pause_stacking(self, event=None):
        if self._stack_job is not None:
            self.border_window.after_cancel(self._stack_job)
            self._stack_job = None

    def _resume_stacking(self, event=None):
        if self._stack_job is None:
            self._keep_border_on_top()

    def toggle_close_button(self):
        # Same withdraw/deiconify + flag flip MainSideMenu.toggle_collapse
        # uses for button_bar, just targeting close_button instead.
        # Reposition/relabel the tab FIRST, so it's already snapped flush
        # against the edge the instant the button disappears, rather than
        # hiding the button and only then catching the tab up to it.
        collapsed = not self.close_toggle.collapsed
        self.close_toggle.set_collapsed(collapsed)
        if collapsed:
            self.close_button.withdraw()
        else:
            self.close_button.deiconify()

    def _on_press(self, x_root, y_root):
        self.start_x, self.start_y = x_root, y_root
        self.selection_box.show_at(x_root, y_root, x_root, y_root)
        # Dismiss any leftover popup from a previous selection before
        # starting a new drag.
        self.pop_up.hide()

    def _on_drag(self, x_root, y_root):
        self.selection_box.show_at(self.start_x, self.start_y, x_root, y_root)

    def _on_release(self, x_root, y_root):
        x1, x2 = sorted((self.start_x, x_root))
        y1, y2 = sorted((self.start_y, y_root))

        if (x2 - x1) > 10 and (y2 - y1) > 10:
            # Hide the indicator so its own red border isn't captured in
            # the screenshot, then briefly restore it as visual feedback.
            self.selection_box.hide()
            self.glass_window.update_idletasks()

            # x1..y2 are logical (DPI-unaware) coords; ImageGrab needs real
            # physical pixels, so scale up first or the capture comes out
            # as a smaller, shifted crop instead of the selected area.
            s = self.dpi_scale
            bbox = (int(x1 * s), int(y1 * s), int(x2 * s), int(y2 * s))
            screenshot = ImageGrab.grab(bbox=bbox)
            self.pop_up.set_screenshot(screenshot) # sends image to popup; "save" happens when save button is pressed
            # You're going to have to find a way to send this screenshot to the edit_menu and convert
            # it to a Photo Image so Canvas can use it. Probably just import this class into the
            # edit_menu file and insert the screenshot directly into the photo image method that way. 
            self.selection_box.show_at(x1, y1, x2, y2)

            # Only now — after a real selection was captured on release —
            # does the popup appear, anchored near the selection's
            # bottom-right corner.
            self.pop_up.show_at(x2, y2)
        else:
            self.selection_box.hide()

    def close(self, event=None):
        if self._stack_job is not None:
            self.border_window.after_cancel(self._stack_job)
            self._stack_job = None
        self.close_toggle.destroy()
        self.close_button.destroy()
        self.pop_up.destroy()
        self.selection_box.destroy()
        self.glass_window.destroy()
        self.border_window.destroy()
