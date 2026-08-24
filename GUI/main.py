import customtkinter as ctk
import constants
from home_page import HomePage
from settings_pages import InstructionsPage, DefaultKeybindsPage
from profile_pages import ProfileSettingsPage, AddProfilePage, EditProfilePage



class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # -- App root window -- 
        # Set theme and appearance of root window
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self.title("Documentation Automation")
        self.geometry("500x500")
        #Grid config: Column 0 (Sidebar), Column 1 (Main content)
        #This set's App's own grid (the root window)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        #Track sidebar state (True = open, False = collapsed)
        #Start out closed
        self.sidebar_visible = None

        # The root window has 2 frames/containers: sidebar and content

        # -- Content area -- contains ALL pages
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nsew")
        # Configures each page frame to stretch to fill container
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Persistent Toggle Button (Stays visible in the main view)
        self.toggle_btn = ctk.CTkButton(
            self.content, 
            text="☰", 
            width=40, 
            height=40, 
            command=self.toggle_sidebar,
            font=("Arial", 18)
        )
        self.toggle_btn.grid(row = 0, column = 0, sticky="nw", pady=10, padx=10, )

        # -- Sidebar Frame
        if ctk.get_appearance_mode() == "Dark":
            self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color = constants.DARK_FG_COLOR)
            self.sidebar.grid_propagate(False)
        else:
            self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color = constants.LIGHT_FG_COLOR)
            self.sidebar.grid_propagate(False)

        # -- Sidebar content 
        self.recording_label = ctk.CTkLabel(self.sidebar, 
            text="Recording",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold", underline=True))
        self.recording_label.pack(pady=0, padx=(15,0), anchor="w") 

        self.make_sidebar_button("Home", lambda: self.show_page(HomePage))

        self.recording_label = ctk.CTkLabel(self.sidebar, 
            text="Settings",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold", underline=True))
        self.recording_label.pack(pady=0, padx=(15,0), anchor="w") 

        self.make_sidebar_button("Instructions", lambda: self.show_page(InstructionsPage))
        self.make_sidebar_button("Default Keybinds", lambda: self.show_page(DefaultKeybindsPage))
        self.make_sidebar_button("Profile Settings", lambda: self.show_page(ProfileSettingsPage))
       
        # Building a dictionary of page instances 
        self.pages= {} 
        for PageClass in (HomePage, InstructionsPage, DefaultKeybindsPage, 
                          ProfileSettingsPage, AddProfilePage, EditProfilePage):
            # Passes the content from App and a dynamic data variable from App (self)
            page = PageClass(self.content, self) # Creates an instance of the loaded class
            # container frame is sent App -> PageClass -> MakeBasePage and processed -> PageClass
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[PageClass] = page # Stores page instance in dictionary
            # Instance's key is its class 

        self.show_page(HomePage)
        self.toggle_btn.lift()

    # -- Functions -- 

    def show_page(self, page_class):
        self.pages[page_class].tkraise()
        self.toggle_btn.lift()

    def make_sidebar_button(self, text, command):
        if ctk.get_appearance_mode() == "Dark":
            sidebar_btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                text_color="white",
                command=command,
                fg_color = "transparent",
                anchor="w"
            )
            sidebar_btn.pack(pady=0, padx=10, fill="x")
            return sidebar_btn
        else: 
            sidebar_btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                text_color="black",
                command=command,
                fg_color = "transparent",
                anchor="w"
            )
            sidebar_btn.pack(pady=0, padx=10, fill="x")
            return sidebar_btn

    def toggle_sidebar(self):
        """Toggles the sidebar visibility and adjusts layout grid dynamically."""
        if self.sidebar_visible:
            # Hide the sidebar completely
            self.sidebar.grid_forget()
            self.sidebar_visible = False
        else:
            # Show the sidebar again in column 0
            self.sidebar.grid(row=0, column=0, sticky="nsew")
            self.sidebar_visible = True



if __name__ == "__main__":
    app = App()
    app.mainloop()









