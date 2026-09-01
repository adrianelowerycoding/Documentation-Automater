from PIL import ImageGrab
import customtkinter as ctk

app = ctk.CTk()
app.geometry("500x500")

start_x = start_y = cur_x = cur_y = 0
rect_id = None


def on_button_press(event):
  global start_x, start_y, rect_id
  start_x, start_y = event.x, event.y

  if rect_id:
    canvas.delete(rect_id)

  rect_id = canvas.create_rectangle(
      start_x, start_y, start_x, start_y, outline="red", width=2
  )


def on_move_press(event):
  global cur_x, cur_y
  cur_x, cur_y = event.x, event.y
  canvas.coords(rect_id, start_x, start_y, cur_x, cur_y)


# --- Automatic Capture Handler ---
def on_button_release(event):
  global cur_x, cur_y
  # Update final mouse coordinates upon release
  cur_x, cur_y = event.x, event.y

  app.update()

  # Calculate global coordinates
  canvas_root_x = canvas.winfo_rootx()
  canvas_root_y = canvas.winfo_rooty()

  x1 = canvas_root_x + min(start_x, cur_x)
  y1 = canvas_root_y + min(start_y, cur_y)
  x2 = canvas_root_x + max(start_x, cur_x)
  y2 = canvas_root_y + max(start_y, cur_y)

  # Enforce minimum size to avoid accidental click crashes
  if (x2 - x1) > 10 and (y2 - y1) > 10:
    # Temporarily hide the selection box outline so it isn't in the screenshot
    canvas.itemconfig(rect_id, outline="")
    app.update()

    # Capture and save
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    screenshot.save("auto_selection.png")
    print("Saved auto_selection.png")

    # Restore the rectangle outline visible on screen
    canvas.itemconfig(rect_id, outline="red")


# UI Setup
canvas = ctk.CTkCanvas(app, bg="#2b2b2b", highlightthickness=0)
canvas.pack(fill="both", expand=True, padx=20, pady=20)

# Bindings
canvas.bind("<ButtonPress-1>", on_button_press)
canvas.bind("<B1-Motion>", on_move_press)
canvas.bind("<ButtonRelease-1>", on_button_release)  # Triggers when drag ends

app.mainloop()
