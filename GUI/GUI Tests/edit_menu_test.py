import customtkinter as ctk

class EditMenu(ctk.CTkToplevel): 
    def __init__(self, master): 
        super().__init__(master)
        self.geometry("1000x600") 

        image_container = ctk.CTkFrame(self, width=800, height=400)
        image_container.pack(pady=20)
        image_container.pack_propagate(False) # Prevent the frame from resizing to fit its content
        

if __name__ == "__main__": 
    root = ctk.CTk()
    root.geometry("600x600")

    status_label = ctk.CTkLabel(root, text="Edit Menu Test")
    status_label.pack(pady=(20,10))

    def launch_edit_menu():
        edit_menu = EditMenu(root)
        edit_menu.grab_set()  # Make the edit menu modal

    launch_button = ctk.CTkButton(root, text="Launch Edit Menu", command=launch_edit_menu)
    launch_button.pack(pady=(10,20))

    root.mainloop()