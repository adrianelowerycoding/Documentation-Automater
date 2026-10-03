from dataclasses import dataclass, field
from docx import Document

@dataclass
class Run: 
    text: str
    bold: bool = False
    italic: bool = False

@dataclass
class Block: 
    kind: str = "paragraph"
    level: int = 1
    # Produces a new list for each Block
    runs: list = field(default_factory=list)

class DocumentCreation(): 
    def __init__(self, words, button_history): 
        super().__init__()

        # pass words and button_history
        self.words = words
        self.button_history = button_history
        self.events = sorted(self.words + self.button_history)


    def build_blocks(self):
        blocks = []
        current = Block()
        italic = False

        for event in self.events: 
            match event: 
                #Matches tuple with 3 items: 
                #heading, italic, bullet, arrow
                case (timestamp, kind, value): 
                    if kind == "word": 
                            pass
                    elif kind == "heading": 
                        current.kind = "heading"
                        current.level = value
                    elif kind == "italic_on":
                        italic = True
                    elif kind == "italic_off":
                        italic = False
                    elif kind == "bullet":
                        pass
                    elif kind == "arrow":
                        pass
                    
                #Matches tuple with 4 items: 
                #screenshot
                case (timestamp, sct_counter, screenshot, filepath):
                    pass


            
    







