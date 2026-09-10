"""

This test actually works.

Standalone, runnable capture overlay: three Toplevels.

WHY THREE WINDOWS:

  -alpha is a per-window compositing value in Tk: every pixel drawn in that
  window — including anything you draw on its canvas — gets faded by the
  SAME amount. There is no way to keep a window's background at 2% opacity
  while a rectangle drawn on that same window's canvas stays fully opaque.
  That's the bug that hit the previous version: the red selection rectangle
  was really being drawn, just at ~2% opacity along with everything else on
  GlassWindow, so it was practically invisible.

  -transparentcolor is the opposite kind of constraint: it punches a literal
  hole wherever an exact color appears, and Windows excludes those pixels
  from hit-testing entirely — so a transparentcolor area is BOTH see-through
  AND click-through, unconditionally. You can't make it see-through but
  still clickable.

  So each visual need gets its own window, because no single Tk window
  property can do more than one of these at once:

    BorderWindow  — solid opaque border, colorkeyed hole in the middle.
                    Always on top. The hole is see-through AND click-through,
                    letting clicks fall through to whatever's beneath it.

    GlassWindow   — low alpha (see-through, but NOT click-through — alpha
                    windows stay fully hit-testable). This is the ONLY
                    window that handles mouse events. It draws nothing
                    visible anymore (see above for why that never worked).

    SelectionBox  — a small, fully-opaque colorkeyed window (same trick as
                    BorderWindow, just resized to the drag box instead of
                    staying fullscreen) that is the actual visible rectangle
                    indicator. It's purely cosmetic: it never binds any
                    mouse events, and it doesn't need to, because once a
                    <Button-1> press starts on GlassWindow, Tk keeps routing
                    <B1-Motion>/<ButtonRelease-1> to that same widget for
                    the rest of the drag no matter what else is stacked on
                    top of it (implicit mouse grab). So SelectionBox can
                    sit visually above GlassWindow without stealing any of
                    its events.

  Stack order top to bottom: BorderWindow > SelectionBox > GlassWindow >
  real desktop.
"""

import customtkinter as ctk
import tkinter as tk
from PIL import ImageGrab


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

        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        save_btn = ctk.CTkButton(self, text="Save", fg_color="blue")
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


class CaptureOverlay:
    """Owns all four windows, keeps them stacked correctly, closes them together."""
    def __init__(self, master, border_color="#FF5733", border_thickness=6):
        self.border_window = BorderWindow(master, border_color, border_thickness)
        self.selection_box = SelectionBox(master, color="red", thickness=2)
        self.glass_window = GlassWindow(
            master,
            on_press=self._on_press,
            on_drag=self._on_drag,
            on_release=self._on_release,
        )
        self.pop_up = EditPopUp(master)

        self.start_x = self.start_y = 0

        self.border_window.bind("<Escape>", self.close)
        self.glass_window.bind("<Escape>", self.close)

        self._stack_job = None
        self._keep_border_on_top()

    def _keep_border_on_top(self):
        # Matches the original known-working pattern: only BorderWindow
        # needs periodic re-lifting to counter the OS/WM occasionally
        # reshuffling -topmost windows. SelectionBox and GlassWindow don't
        # need to be forced into position relative to it — SelectionBox is
        # created after BorderWindow (so it's already above it in initial
        # stacking) and GlassWindow's clicks are routed by widget identity
        # during a drag, not by current z-order.
        self.border_window.lift()
        self._stack_job = self.border_window.after(50, self._keep_border_on_top)

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

            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            screenshot.save("auto_selection.png")
            print("Saved auto_selection.png")

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
        self.pop_up.destroy()
        self.selection_box.destroy()
        self.glass_window.destroy()
        self.border_window.destroy()


if __name__ == "__main__":
    # Standalone test harness — run this file directly, no main app needed.
    root = ctk.CTk()
    root.title("CaptureOverlay test harness")
    root.geometry("300x120")

    status_label = ctk.CTkLabel(
        root,
        text="Click 'Launch Overlay', then drag a box.\nEsc closes the overlay.",
    )
    status_label.pack(pady=(20, 10))

    def launch_overlay():
        CaptureOverlay(root)  # root = the running CTk instance; no second
                               # root or mainloop needed, rides this one

    launch_btn = ctk.CTkButton(root, text="Launch Overlay", command=launch_overlay)
    launch_btn.pack(pady=5)

    root.mainloop()

# --- Wiring into your real App later ---
#
#     self.make_sidebar_button("Capture", lambda: CaptureOverlay(self))
#
# self = the running App/CTk root — no new root or mainloop needed, it
# rides your existing app.mainloop().