import customtkinter as ctk
from base_page import MakeBasePage
import constants

class ProfileSettingsPage(MakeBasePage):
    def __init__(self, content, controller):
        super().__init__(content, controller)

        self.make_title("Profile Settings")
        current_profile_label = ctk.CTkLabel(
            self,
            text="Loaded:",
            font=constants.SUBTITLE_FONT,
        )
        current_profile_label.grid(row=1, column=0, padx=0, pady=(0,10))
        # Profiles 
        # profiles_btn = ctk.CTkOptionMenu(
        #     values=
        # )
        self.make_nav_button("Add Profile", lambda: self.controller.show_page(AddProfilePage), True, 3)
        self.make_nav_button("Edit Profile", lambda: self.controller.show_page(EditProfilePage), True, 4)
        self.make_nav_button("Remove Profile", None, True, 5)

class AddProfilePage(MakeBasePage):
    def __init__(self,content, controller):
        super().__init__(content, controller)
        self.make_title("Add Profile")

        # -- Profile Name Entry -- 
        self.profile_name_label = ctk.CTkLabel(self, text="Profile Name:", font=("Arial", 11, "bold"))
        self.profile_name_label.grid(row=1, column=0, sticky="w", padx=20)
        self.profile_name_entry = ctk.CTkEntry(self, height=20, placeholder_text="Enter Profile Name...")
        self.profile_name_entry.grid(row=1, column=0, sticky="w",padx=100, pady=20)

        # -- Keybinds -- 
        self.set_keybinds_line("Keybind 1", None, 2, 2)
        self.set_keybinds_line("Keybind 2", None, 3, 2)


class EditProfilePage(MakeBasePage):
    def __init__(self,content, controller):
        super().__init__(content, controller)
        self.make_title("Edit Profile")

        # -- Profile Name -- 
        self.profile_name_label = ctk.CTkLabel(self, text="Profile:", font=("Arial", 11, "bold"))
        self.profile_name_label.grid(row=1, column=0, sticky="w", padx=20, pady=20)
        self.profile_name_label = ctk.CTkLabel(self, text=self.fetch_data(1), font=("Arial", 11, "bold"))
        self.profile_name_label.grid(row=1, column=0, sticky="w", padx=65, pady=20)

        # -- Command Keybinds -- 
        self.set_keybinds_line("Keybind 1", None, 2, 2)
        self.set_keybinds_line("Keybind 2", None, 3, 2)
