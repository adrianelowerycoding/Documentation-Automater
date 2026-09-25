"""
This test shows how to create the button_history[] list by pressing 
command buttons.
"""

import customtkinter as ctk

is_pressed = False
button_history = []

def on_press(): 
    global is_pressed

    if is_pressed == False:
        is_pressed = True
        button_history.append(("time", "heading_on", "value"))

        button.configure(
            fg_color="blue"
        )
        print("is_pressed =", is_pressed)
        print(button_history)

    elif is_pressed == True:
        is_pressed = False
        button_history.append(("time", "heading_off", "value"))

        button.configure(
            fg_color="white"
        )
        print("is_pressed =", is_pressed)
        print(button_history)


root = ctk.CTk()
root.title("Click example")
root.geometry("250x150")

button = ctk.CTkButton(
    root,
    fg_color="white",
    hover=False,
    text="Click",
    command=on_press
)

button.pack(expand=True)
root.mainloop()