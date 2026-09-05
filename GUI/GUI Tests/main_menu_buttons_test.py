import customtkinter as ctk
from PIL import Image

app = ctk.CTk()
app.geometry("200x200")

img = Image.open(r"c:\Users\adria\Documents\Coding\Python\Big Projects\SOP Automater\Documentation-Automer-\Assets\Heading_icon.png")
print("PIL image size/mode:", img.size, img.mode)

ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(20, 20))

btn = ctk.CTkButton(app, text="", image=ctk_img)
btn.pack(padx=20, pady=20)

app.mainloop()