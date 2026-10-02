import customtkinter as ctk
from base_page import MakeBasePage
from enum import Enum, auto
import constants
from recording_state import RecordingState
from main_side_menu import MainSideMenu
from new_guide_window import NewGuideWindow
from Guts.Controller import Controller

"""
CURRENT PROB: After I save or clear the first file all of the "disableds" are turned off. I'm able to click the pause, stop, save, and clear buttons.
After saving or clearing a file the page should return to the default original state.
"""


# Create function to create recording buttons

# This describes inheritance
class HomePage(MakeBasePage): # Homepage Extends MakeBasePage

    HOMEPAGE_BUTTON_CONFIG = {
        RecordingState.RECORDING: {
            "record_btn": {"fg_color": "#E74C3C", "state": "disabled", "text_color_disabled": "white"},
            "pause_btn": {"fg_color": "#1F6AA5", "state": "normal", "hover": True},
            "stop_btn": {"fg_color": "#1F6AA5", "state": "normal", "hover": True},
            "output_btn": {"text": "● Recording", "font": constants.OUTPUT_BTN_FONT, "fg_color": "#E74C3C", "hover": False}
        },
        RecordingState.PAUSED: {
            "record_btn": {"fg_color": "#1F6AA5", "state": "normal", "hover": True},
            "pause_btn": {"fg_color": "#FFB100", "state": "disabled", "text_color_disabled": "white"},
            "output_btn": {"text": "⏸Paused", "font": constants.OUTPUT_BTN_FONT, "fg_color": "#FFB100", "hover": False}
        },
        RecordingState.STOPPED: {
            "record_btn": {"fg_color": "#1F6AA5", "state": "disabled", "text_color_disabled": "white"},
            "pause_btn": {"fg_color": "#1F6AA5", "state": "disabled", "text_color_disabled": "white"},
            "stop_btn": {"fg_color": "#374151", "state": "disabled", "text_color_disabled": "white"},
            "output_btn": {"text": "⏹ Stopped", "font": constants.OUTPUT_BTN_FONT, "fg_color": "#374151", "hover": False},
            "save_btn": {"state": "normal"},
            "clear_btn": {"state": "normal"}
        },
        RecordingState.SAVED: {
            "record_btn": {"fg_color": "#1F6AA5", "state": "normal"},
            "pause_btn": {"fg_color": "#1F6AA5", "state": "disabled", "text_color_disabled": "white"},
            "stop_btn": {"fg_color": "#1F6AA5", "state": "disabled", "text_color_disabled": "white"},
            "output_btn": {"text": None, "fg_color": "#184669", "state": "disabled", "text_color_disabled": "white"},
            "save_btn": {"state": "disabled", "text_color_disabled": "white"},
            "clear_btn": {"state": "disabled", "text_color_disabled": "white"}
        },
        RecordingState.CLEARED: {
            "record_btn": {"fg_color": "#1F6AA5", "state": "normal"},
            "pause_btn": {"fg_color": "#1F6AA5", "state": "disabled", "text_color_disabled": "white"},
            "stop_btn": {"fg_color": "#1F6AA5", "state": "disabled", "text_color_disabled": "white"},
            "output_btn": {"text": None, "fg_color": "#184669", "state": "disabled", "text_color_disabled": "white"},
            "save_btn": {"state": "disabled", "text_color_disabled": "white"},
            "clear_btn": {"state": "disabled", "text_color_disabled": "white"}
        }

    }

    # This is what info needed when this class is built as an object
    # making an object HomePage(content)
    def __init__(self, content, controller):
        # super() is a 2 way call; receives and sends data to the parent
        super().__init__(content, controller) # call parent class and give it data in the parameter

        # All frames and elements (recording_button_frame, save_button_frame, output_btn)
        # on this page sit in the HomePage frame

        self.main_side_menu = None # Tracking toplevel for on_click_record
        self.new_guide_window = None # Tracking toplevel for on_click_new_guide
        self.current_guide_path = None # Folder of the guide the user just made
        self.controller = None # the ONE Controller for the current recording session - built in on_click_record
        # -- Prepping Page --
        ## -- Layout: top bar, top spacer, title, output, recording, save/clear, bottom spacer, status bar --
        self.columnconfigure(0, weight=1) # only 1 column, this keeps everything centered in the window
        self.rowconfigure(0, weight=0) # row 0: top_bar (New Guide button)
        self.rowconfigure(1, weight=1) # row 1: top spacer
        self.rowconfigure(2, weight=0) # row 2: title
        self.rowconfigure(3, weight=0) # row 3: output_btn
        self.rowconfigure(4, weight=0) # row 4: recording_button_frame
        self.rowconfigure(5, weight=0) # row 5: save_button_frame
        self.rowconfigure(6, weight=1) # row 6: Bottom spacer
        self.rowconfigure(7, weight=0) # row 7: status_bar (project + guide loaded)

        ## -- Ribbon across the top, New Guide button lives here --
        ## (toggle button is up in the header above this, so they don't stack on each other anymore)
        top_bar = ctk.CTkFrame(self, height=44, corner_radius=0)
        top_bar.grid(row=0, column=0, sticky="ew")

        self.new_guide_btn = ctk.CTkButton(
            top_bar,
            text="New Guide",
            command=self.on_click_new_guide,
            width=100,
            height=28,
            corner_radius=8
            )
        self.new_guide_btn.grid(row=0, column=0, sticky="w", padx=10, pady=8)

        ## -- Creating status bar along the bottom that shows what's loaded --
        status_bar = ctk.CTkFrame(self, height=28, corner_radius=0)
        status_bar.grid(row=7, column=0, sticky="ew")

        # keeping this small and gray so it doesn't fight the title for attention
        self.loaded_label = ctk.CTkLabel(status_bar, text="Project Loaded: None | Current Guide: None", font=("Arial", 12), text_color="gray60")
        self.loaded_label.grid(row=0, column=0, padx=10, pady=4, sticky="w")

        ## -- Creating frame for recording buttons --
        recording_button_frame = ctk.CTkFrame(self, width=constants.BUTTON_WIDTH, height=36, fg_color="transparent")
        recording_button_frame.grid(row=4, column=0, pady=(0,10))
        recording_button_frame.grid_propagate(False)
        ## -- Configuring column weights for recording frame --
        recording_button_frame.columnconfigure(0, weight=1) # record's col
        recording_button_frame.columnconfigure(1, weight=1) # pause's col
        recording_button_frame.columnconfigure(2, weight=1) # stop's col

        ## -- Creating frame for Save and Clear buttons --
        save_button_frame = ctk.CTkFrame(self, width=constants.BUTTON_WIDTH, height=24, fg_color="transparent")
        save_button_frame.grid(row=5, column=0, pady=(0,0))
        save_button_frame.grid_propagate(False)
        save_button_frame.columnconfigure(0, weight=1) # Save's col
        save_button_frame.columnconfigure(1, weight=1) # Clear's col

        # -- Laying out Page --
        # self.make_title("Documentation Automater")
        self.home_page_title = ctk.CTkLabel(self, text="Documentation Automater", font=("Arial", 24, "bold"))
        self.home_page_title.grid(row=2, column=0, pady=(0,10))

        # self.output_btn = self.make_nav_button(None, self.on_click_record, False, 2) # pass it a command that's listening for 3 different values
        self.output_btn = ctk.CTkButton(
            self,
            fg_color="#184669",
            text=None,
            state="disabled",
            text_color_disabled="white",
            command=self.on_click_record,
            width=constants.BUTTON_WIDTH,
            height=constants.BUTTON_HEIGHT,
            corner_radius=20,
            hover=False
            )
        self.output_btn.grid(row=3, column=0, pady=(0,10))

        # record starts disabled, on_guide_created flips it on once you actually have a guide to record into
        self.record_btn = self.make_recording_button(recording_button_frame,"●",self.on_click_record, "disabled", 0)
        self.pause_btn = self.make_recording_button(recording_button_frame,"⏸",self.on_click_pause, "disabled",1)
        self.stop_btn = self.make_recording_button(recording_button_frame,"⏹",self.on_click_stop, "disabled", 2)
        self.save_btn = self.make_save_button(save_button_frame, "Save", self.on_click_save, 0)
        self.clear_btn = self.make_save_button(save_button_frame, "Clear", self.on_click_clear, 1)

    # -- HomePage Functions --
    def make_recording_button(self, master, text, command, state, column):
        btn = ctk.CTkButton(
            master,
            text=text,
            font=("Arial", 18),
            command=command, # Each button has dif commmand; impacts the output button
            state=state,
            hover=True,
            text_color_disabled="white",
            width=46,
            height=36,
            corner_radius=8,
            )
        #btn.grid(row=0, column=0, sticky="w", padx=padx, pady=8)
        btn.grid(row=0, column=column)
        return btn

    def make_save_button(self, master, text, command, column):
        btn = ctk.CTkButton(
            master,
            text=text,
            command=command, # Each button has dif commmand; impacts the output button
            state="disabled",
            text_color_disabled="white",
            width=85,
            height=24,
            corner_radius=8,
            )
        #btn.grid(row=0, column=0, sticky="w", padx=padx, pady=8)
        btn.grid(row=0, column=column)
        return btn

    def set_state(self, new_state: RecordingState):
        self.state = new_state
        config = self.HOMEPAGE_BUTTON_CONFIG[new_state]
        for btn_name, kwargs in config.items():
            getattr(self, btn_name).configure(**kwargs)

    def on_click_new_guide(self):
        # If the New Guide window isn't open, open it. If it is, just bring it to the front
        # (it checks the JSON file for the root folder by itself when it opens)
        if self.new_guide_window is None or not self.new_guide_window.winfo_exists():
            self.new_guide_window = NewGuideWindow(self, self.on_guide_created)
        else:
            self.new_guide_window.lift()

    def on_guide_created(self, guide_path):
        # fires when Create is clicked in NewGuideWindow, stashing the path for the recording side to use
        self.current_guide_path = guide_path

        # parent of the guide folder IS the project folder so this grabs both names in one shot
        project_name = guide_path.parent.name
        guide_name = guide_path.name
        self.loaded_label.configure(text=f"Project Loaded: {project_name} | Current Guide: {guide_name}", text_color=("gray10", "gray90"))

        # don't flip Record on if a recording is already happening
        # (self.state doesn't exist til set_state() runs once, hence the getattr instead of self.state directly)
        if getattr(self, "state", None) in (None, RecordingState.SAVED, RecordingState.CLEARED):
            self.record_btn.configure(state="normal")

    def on_click_record(self):
        # Sets state to recording and opens main_side_menu
        self.set_state(RecordingState.RECORDING)
        # If main_side_menu isn't open, open it and lift it
        if self.main_side_menu is None or not self.main_side_menu.winfo_exists():
            # only making ONE Controller now, right here. gets passed down to MainSideMenu,
            # then to CaptureOverlay/EditMenu - nothing else builds its own anymore
            self.controller = Controller(self.current_guide_path)
            self.main_side_menu = MainSideMenu(self, controller=self.controller)
            self.controller.start_recording()
        else:
            self.main_side_menu.lift()

    def on_click_pause(self):
        self.set_state(RecordingState.PAUSED)

    def on_click_stop(self):
        # Stops the recording and destroys main_side_menu
        self.set_state(RecordingState.STOPPED)
        self.main_side_menu.destroy()

    def on_click_save(self):
        self.set_state(RecordingState.SAVED)

    def on_click_clear(self):
        self.set_state(RecordingState.CLEARED)