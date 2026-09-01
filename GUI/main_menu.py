import customtkinter as ctk 

main_side_menu = ctk.CTk()
main_side_menu.attributes("-topmost", True)
ctk.set_default_color_theme("blue")
main_side_menu.overrideredirect(True)
# 1. Define your desired window dimensions
window_width = 400
window_height = 500

# 2. Fetch the native monitor dimensions
screen_width = main_side_menu.winfo_screenwidth()
screen_height = main_side_menu.winfo_screenheight()

# 3. Calculate the coordinates for the middle-right placement
x_position = screen_width - window_width
y_position = (screen_height - window_height) // 2

# 4. Apply the geometry string format: "widthxheight+x+y"
main_side_menu.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

if __name__ == "__main__":
    main_side_menu.mainloop()


