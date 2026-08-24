from base_page import MakeBasePage

class InstructionsPage(MakeBasePage):
    def __init__(self, content, controller):
        super().__init__(content, controller)
        self.make_title("Instructions")

        #scrollable README doc

class DefaultKeybindsPage (MakeBasePage):
    def __init__(self, content, controller):
        super().__init__(content, controller)
        self.make_title("Default Keybinds")

        # -- Keybinds -- 
        self.make_command_label("Keybind 1", 1, 2)
        self.make_command_label("Keybind 2", 2, 2)