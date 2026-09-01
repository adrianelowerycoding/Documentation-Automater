import customtkinter as ctk

screenshot_window = ctk.CTk()

border_color = "#FF5733"
border_thickness = 6  # px — change this to whatever you want

screenshot_window.attributes("-fullscreen", True)
screenshot_window.overrideredirect(True)
screenshot_window.attributes("-topmost", True)

screenshot_window.attributes("-alpha", 1)

# Outer frame = the border color, fills the whole window
border_frame = ctk.CTkFrame(screenshot_window, fg_color=border_color, corner_radius=0)
border_frame.pack(fill="both", expand=True)

# Inner frame = transparent, inset by border_thickness on all sides
# so the outer frame's color peeks out as a ring around it
inner_frame = ctk.CTkFrame(border_frame, fg_color="transparent", corner_radius=0)
inner_frame.pack(fill="both", expand=True, padx=border_thickness, pady=border_thickness)

screenshot_window.bind("<Escape>", lambda event: screenshot_window.attributes("-fullscreen", False))

screenshot_window.mainloop()