import customtkinter as ctk
from base_page import MakeBasePage
import constants

"""
CURRENT PROB: After I save or clear the first file all of the "disableds" are turned off. I'm able to click the pause, stop, save, and clear buttons. 
After saving or clearing a file the page should return to the default original state. 
"""


# Create function to create recording buttons

# This describes inheritance
class HomePage(MakeBasePage): # Homepage Extends MakeBasePage
    # This is what info needed when this class is built as an object
    # making an object HomePage(content)
    def __init__(self, content, controller):
        # super() is a 2 way call; receives and sends data to the parent
        super().__init__(content, controller) # call parent class and give it data in the parameter

        # All frames and elements (recording_button_frame, save_button_frame, output_btn) 
        # on this page sit in the HomePage frame

        # -- Prepping Page -- 
        ## -- Centering elements and 
        self.rowconfigure(0, weight=1) # row 0: top spacer
        self.rowconfigure(1, weight=0) # row 1: title
        self.rowconfigure(2, weight=0) # row 2: output_btn 
        self.rowconfigure(3, weight=0) # row 3: recording_button_frame
        self.rowconfigure(4, weight=0) # row 4: save_button_frame
        self.rowconfigure(5, weight=1) # row 5: Bottom spacer
        
        ## -- Creating frame for recording buttons -- 
        recording_button_frame = ctk.CTkFrame(self, width=constants.BUTTON_WIDTH, height=36, fg_color="transparent")
        recording_button_frame.grid(row=3, column=0, pady=(0,10))
        recording_button_frame.grid_propagate(False)
        ## -- Configuring column weights for recording frame -- 
        recording_button_frame.columnconfigure(0, weight=1) # record's col
        recording_button_frame.columnconfigure(1, weight=1) # pause's col
        recording_button_frame.columnconfigure(2, weight=1) # stop's col

        ## -- Creating frame for Save and Clear buttons -- 
        save_button_frame = ctk.CTkFrame(self, width=constants.BUTTON_WIDTH, height=24, fg_color="transparent")
        save_button_frame.grid(row=4, column=0, pady=(0,0))
        save_button_frame.grid_propagate(False)
        save_button_frame.columnconfigure(0, weight=1) # Save's col
        save_button_frame.columnconfigure(1, weight=1) # Clear's col
        
        # -- Laying out Page --
        # self.make_title("Documentation Automater")
        self.home_page_title = ctk.CTkLabel(self, text="Documentation Automater", font=("Arial", 24, "bold"))
        self.home_page_title.grid(row=1, column=0, pady=(0,10))
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
        self.output_btn.grid(row=2, column=0, pady=(0,10))

        self.record_btn = self.make_recording_button(recording_button_frame,"●",self.on_click_record, "normal", 0)
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

    def on_click_record(self): 
        self.record_btn.configure(
            fg_color="#E74C3C",
            hover=False,
            state="disabled",
            text_color_disabled="white"
        )
        self.pause_btn.configure(
            fg_color="#1F6AA5",
            state="normal",
            hover=True,
        )
        self.stop_btn.configure(
            fg_color="#1F6AA5",
            state="normal",
            hover=True,
        )

        self.output_btn.configure(
        text="● Recording", 
        font=("Arial", 14, "bold"),
        fg_color = "#E74C3C",
        hover=False,
        )

    def on_click_pause(self):
        self.pause_btn.configure(
            fg_color="#FFB100",
            hover=False,
            state = "disable",
            text_color_disabled = "white",
        )
        self.record_btn.configure(
            fg_color="#1F6AA5",
            state="normal",
            hover=True
        )
        self.output_btn.configure(
            text="⏸Paused",
            font=("Arial", 14, "bold"),
            fg_color = "#FFB100",
            hover=False,
        )

    def on_click_stop(self):
        self.stop_btn.configure(
            fg_color="#374151",
            hover=False,
            state="disable",
            text_color_disabled = "white",
        )
        self.record_btn.configure(
            fg_color="#1F6AA5",
            state="disabled",
            text_color_disabled="white"
        )
        self.pause_btn.configure(
            fg_color="#1F6AA5",
            state="disabled",
            text_color_disabled="white"
        )
        self.output_btn.configure(
            text="⏹ Stopped",
            font=("Arial", 14, "bold"),
            fg_color = "#374151",
            hover=False,
        )
        self.save_btn.configure(
            state="normal"
        )
        self.clear_btn.configure(
            state="normal"
        )

    def on_click_save(self): 
        self.stop_btn.configure(
            fg_color="#1F6AA5",
            state="normal"
        )
        self.record_btn.configure(
            fg_color="#1F6AA5",
            state="normal"
        )
        self.pause_btn.configure(
            fg_color="#1F6AA5",
            state="normal"
        )
        self.output_btn.configure(
            text=None,
            fg_color="#184669",
            state="disabled",
            text_color_disabled="white",
            hover=False,
        )

    def on_click_clear(self): 
        self.stop_btn.configure(
            fg_color="#1F6AA5",
            state="normal"
        )
        self.record_btn.configure(
            fg_color="#1F6AA5",
            state="normal"
        )
        self.pause_btn.configure(
            fg_color="#1F6AA5",
            state="normal"
        )
        self.output_btn.configure(
            text=None,
            fg_color="#184669",
            state="disabled",
            text_color_disabled="white",
            hover=False,
        )


    