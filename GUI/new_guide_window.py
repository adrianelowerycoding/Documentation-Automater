import re
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk
from settings_manager import get_root_folder, set_root_folder

# Characters Windows doesn't allow in folder names
INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# Text the option menu shows before the user picks something
LOAD_TEXT = "Load"
EMPTY_TEXT = "No projects yet"


class RootFolderPrompt(ctk.CTkToplevel):
    # Small popup that asks the user where the root Projects folder should go
    def __init__(self, parent, on_saved, on_cancel):
        super().__init__(parent)
        self.on_saved = on_saved
        self.on_cancel = on_cancel

        self.title("Select Root Folder")
        self.geometry("480x170")
        self.resizable(False, False)
        self.transient(parent) # keeps this window on top of the New Guide window

        # Closing with the X counts as canceling
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.columnconfigure(0, weight=1)

        # -- Message at the top --
        message = ctk.CTkLabel(self, text="Root folder not selected yet. Please select one now.")
        message.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # -- Text box with the default path already filled in --
        self.path_entry = ctk.CTkEntry(self)
        self.path_entry.grid(row=1, column=0, padx=(20, 5), sticky="ew")
        self.path_entry.insert(0, str(Path.home() / "Documents" / "Documentation_Automater" / "Projects"))

        # -- Browse button sits right next to the text box --
        browse_btn = ctk.CTkButton(self, text="Browse", width=80, command=self.on_click_browse)
        browse_btn.grid(row=1, column=1, padx=(0, 20))

        # -- Red text for errors, empty until something goes wrong --
        self.error_label = ctk.CTkLabel(self, text="", text_color="#E74C3C")
        self.error_label.grid(row=2, column=0, columnspan=2, padx=20, pady=(5, 0), sticky="w")

        # -- Save button in the bottom right --
        save_btn = ctk.CTkButton(self, text="Save", width=80, command=self.on_click_save)
        save_btn.grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 15), sticky="e")

        # CTkToplevel can pop up behind the parent on Windows, so lift it after it's drawn
        self.after(200, self.lift_and_grab)

    def lift_and_grab(self):
        # grab_set makes the user deal with this window before touching anything else
        self.lift()
        self.focus()
        self.grab_set()

    def on_click_browse(self):
        # Open File Explorer starting at whatever is in the text box
        start = self.path_entry.get().strip() or str(Path.home())
        chosen = filedialog.askdirectory(initialdir=start, title="Select Root Folder", parent=self)
        if chosen:
            # Swap the text box contents with the folder they picked
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, str(Path(chosen)))

    def on_click_save(self):
        path = self.path_entry.get().strip()
        if not path:
            self.error_label.configure(text="Please enter a folder path.")
            return
        # Make the folder if it doesn't exist yet
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except OSError:
            self.error_label.configure(text="Couldn't create that folder. Try a different spot.")
            return
        # Save to the JSON file, then tell the New Guide window we're done
        set_root_folder(path)
        self.grab_release()
        self.on_saved()
        self.destroy()

    def cancel(self):
        self.grab_release()
        self.on_cancel()
        self.destroy()


class NewGuideWindow(ctk.CTkToplevel):
    # The New Guide menu. on_create gets called with the new Guide folder's path
    def __init__(self, parent, on_create=None):
        super().__init__(parent)
        self.on_create = on_create
        self.root_folder = get_root_folder()
        self.root_prompt = None

        self.title("New Guide")
        self.geometry("380x290")
        self.resizable(False, False)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # -- Heading --
        heading = ctk.CTkLabel(self, text="New Guide", font=("Arial", 20, "bold"))
        heading.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 15), sticky="w")

        # -- Project row: label + New button + Load option menu --
        project_label = ctk.CTkLabel(self, text="Project")
        project_label.grid(row=1, column=0, padx=(20, 10), pady=8, sticky="w")

        project_frame = ctk.CTkFrame(self, fg_color="transparent")
        project_frame.grid(row=1, column=1, padx=(0, 20), pady=8, sticky="w")

        self.new_project_btn = ctk.CTkButton(project_frame, text="New", width=60, command=self.on_click_new_project)
        self.new_project_btn.grid(row=0, column=0, padx=(0, 8))

        # Holds whatever project is picked. Starts out saying "Load"
        self.project_var = ctk.StringVar(value=LOAD_TEXT)
        self.project_menu = ctk.CTkOptionMenu(project_frame, variable=self.project_var, values=[EMPTY_TEXT], width=140)
        self.project_menu.grid(row=0, column=1)

        # -- Guide Name row --
        name_label = ctk.CTkLabel(self, text="Guide Name")
        name_label.grid(row=2, column=0, padx=(20, 10), pady=8, sticky="w")

        self.guide_name_entry = ctk.CTkEntry(self, placeholder_text="Type a guide name")
        self.guide_name_entry.grid(row=2, column=1, padx=(0, 20), pady=8, sticky="ew")

        # -- Screenshots Folder row --
        sct_label = ctk.CTkLabel(self, text="Screenshots Folder")
        sct_label.grid(row=3, column=0, padx=(20, 10), pady=8, sticky="w")

        # Just a switch for now, it doesn't do anything yet
        self.screenshot_switch = ctk.CTkSwitch(self, text="")
        self.screenshot_switch.grid(row=3, column=1, padx=(0, 20), pady=8, sticky="w")

        # -- Red text for errors --
        self.error_label = ctk.CTkLabel(self, text="", text_color="#E74C3C")
        self.error_label.grid(row=4, column=0, columnspan=2, padx=20, sticky="w")

        # -- Create button in the bottom right --
        self.create_btn = ctk.CTkButton(self, text="Create", width=90, command=self.on_click_create)
        self.create_btn.grid(row=5, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="e")

        # Fill the option menu if we already have a root folder
        self.refresh_projects()

        # Wait a moment so this window is drawn first, then check for the root folder
        self.after(150, self.check_root_folder)

    # -- Root folder stuff --
    def check_root_folder(self):
        # If there's no root folder saved yet, pop up the prompt on top of this window
        if self.root_folder is None:
            self.root_prompt = RootFolderPrompt(self, self.on_root_saved, self.on_root_canceled)

    def on_root_saved(self):
        # Grab the root folder that was just saved and fill the project list
        self.root_folder = get_root_folder()
        self.refresh_projects()

    def on_root_canceled(self):
        # Can't make guides without a root folder, so close the New Guide window too
        self.destroy()

    # -- Project stuff --
    def refresh_projects(self):
        # Fill the option menu with every folder inside the root folder
        if self.root_folder is None:
            return
        names = sorted(p.name for p in self.root_folder.iterdir() if p.is_dir())
        self.project_menu.configure(values=names or [EMPTY_TEXT])

    def on_click_new_project(self):
        if self.root_folder is None:
            return
        # Small popup where the user types the new project name
        dialog = ctk.CTkInputDialog(text="Project name:", title="New Project")
        name = dialog.get_input()

        # None means they hit cancel, empty means they typed nothing
        if name is None:
            return
        name = name.strip()
        if not name:
            self.error_label.configure(text="Please enter a project name.")
            return
        if INVALID_CHARS.search(name) or name.endswith("."):
            self.error_label.configure(text='Project name can\'t have  < > : " / \\ | ? *')
            return

        # Make the project folder inside the root folder
        # exist_ok=True so typing a name that already exists just selects it
        try:
            (self.root_folder / name).mkdir(exist_ok=True)
        except OSError:
            self.error_label.configure(text="Couldn't create that folder. Check your permissions.")
            return

        self.error_label.configure(text="")
        # Update the list and select the new project
        self.refresh_projects()
        self.project_var.set(name)

    # -- Create button --
    def on_click_create(self):
        project = self.project_var.get()
        guide_name = self.guide_name_entry.get().strip()

        # Check everything before making any folders
        if self.root_folder is None:
            self.error_label.configure(text="Root folder isn't set yet.")
            return
        if project in (LOAD_TEXT, EMPTY_TEXT):
            self.error_label.configure(text="Please pick or create a project.")
            return
        if not guide_name:
            self.error_label.configure(text="Please enter a guide name.")
            return
        if INVALID_CHARS.search(guide_name) or guide_name.endswith("."):
            self.error_label.configure(text='Guide name can\'t have  < > : " / \\ | ? *')
            return

        guide_folder = self.root_folder / project / guide_name
        if guide_folder.exists():
            self.error_label.configure(text="A guide with that name already exists.")
            return

        # Make the Guide folder and the screenshots folder inside it
        # (the switch doesn't do anything yet so the screenshots folder always gets made)
        try:
            guide_folder.mkdir(parents=True)
            (guide_folder / "screenshots").mkdir()
        except OSError:
            self.error_label.configure(text="Couldn't create the folders. Check your permissions.")
            return

        # Let the home page know where the new guide is, then close
        if self.on_create:
            self.on_create(guide_folder)
        self.destroy()