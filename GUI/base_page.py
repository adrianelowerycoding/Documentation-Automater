import customtkinter as ctk
import constants

class MakeBasePage(ctk.CTkFrame):
    def __init__(self, content, controller): #content arrives here
        super().__init__(content, fg_color="transparent") # content gets forwarded onward # same as page = ctk.CTkFrame(container, fg_color="transparent")
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.controller = controller

    def make_title(self, text):
        title = ctk.CTkLabel(self, text=text, font=constants.TITLE_FONT)
        title.grid(row=0, column=0, pady=20)
        # return page? 

    def make_nav_button(self, text, command, hover, row):
            btn = ctk.CTkButton(
                self,
                text=text,
                command=command,
                width=constants.BUTTON_WIDTH,
                height=constants.BUTTON_HEIGHT,
                corner_radius=8,
                hover=hover,
                )
            btn.grid(row=row, column=0, padx=0, pady=8)
            return btn

    # def make_command_listener(self, text, command, row):
    # I've replaced this with set_keybinds_line
    #     command_name_label = ctk.CTkLabel(self, text=text, font=("Arial", 11, "bold"))
    #     command_name_label.grid(row=row, column=0, sticky="w", padx=20, pady=0)

    #     listener_btn = ctk.CTkButton(
    #         self, 
    #         text="Select",
    #         command=command,
    #         width=30,
    #         height=20,
    #         )
    #     listener_btn.grid(row=row, column=0, stick="w", padx=100, pady=0)
    #     return command_name_label, listener_btn

    def make_command_label(self, text, row, signal):

        command_name_label = ctk.CTkLabel(self, text=text, font=("Arial", 11, "bold"))
        command_name_label.grid(row=row, column=0, sticky="w", padx=20, pady=0)

        keybind_label = ctk.CTkLabel(self, text=self.fetch_data(signal), font=("Arial", 11, "bold"))
        keybind_label.grid(row=row, column=0, sticky="w", padx=100, pady=0)

    def set_keybinds_line(self, text, command, row, signal):
        command_name_label = ctk.CTkLabel(self, text=text, font=("Arial", 11, "bold"))
        command_name_label.grid(row=row, column=0, sticky="w", padx=20, pady=0)

        listener_btn = ctk.CTkButton(
            self, 
            text="Select",
            command=command,
            width=30,
            height=20,
            )
        listener_btn.grid(row=row, column=0, stick="w", padx=100, pady=0)

        keybind_label = ctk.CTkLabel(self, text=self.fetch_data(signal), font=("Arial", 11, "bold"))
        keybind_label.grid(row=row, column=0, sticky="w", padx=180, pady=0)

        return command_name_label, listener_btn, keybind_label


    def show_keybind_text(self): # fetch data
        # This should grab the keybind for each label from the database
        keybind_text = "Dummy text; make logic later"
        return keybind_text

    def fetch_data(self, signal): 
        # Very rough and rudimentary early version 
        # final version will use dictionary keys and values
        if signal == 1: 
            profile_name = "Dummy profile name" # return profile name
            return profile_name
        elif signal == 2: 
            keybind_text = "Dummy keybind" # return keybind text
            return keybind_text