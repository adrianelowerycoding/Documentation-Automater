from dataclasses import dataclass, field
from docx import Document
from docx.shared import Inches
from pathlib import Path
from typing import Any

@dataclass
class Run: 
    text: str
    italic: bool = False

@dataclass
class Block: 
    kind: str = "paragraph"
    value: Any = None
    # Produces a new list for each Block
    runs: list = field(default_factory=list)

class DocumentCreation(): 
    def __init__(self, words, button_history): 
        super().__init__()

        # pass words and button_history
        self.words = words
        self.button_history = button_history
        self.events = sorted(self.words + self.button_history)
        self.path = Path.cwd()


    def build_blocks(self):
        self.blocks = []
        self.current = Block()
        self.italic = False

        for event in self.events: 
            match event: 
                #Matches tuple with 3 items: 
                #heading, italic, bullet, arrow
                case (timestamp, kind, value): 
                    if kind == "word" or kind == "arrow": #evaluating both "word" and "arrow" type
                        last = self.current.runs[-1] if self.current.runs else None
                        if last and last.italic == self.italic: 
                            last.text += " " + value
                        else:
                            text = (" " if self.current.runs else "") + value # no leading space on first word
                            self.current.runs.append(Run(text,italic=self.italic))

                    elif kind == "heading":
                        self.current.kind = "heading"
                        self.current.value = value

                    elif kind == "italic_on":
                        self.italic = True

                    elif kind == "italic_off":
                        self.italic = False

                    elif kind == "bullet":
                        self.current.kind = "bullet"
                        self.current.value = value # List Bullet or List Number

                    elif kind == "block_end":
                        self.blocks.append(self.current)
                        self.current = Block()
                    
                #Matches tuple with 4 items: 
                #screenshot
                case (timestamp, sct_counter, kind, filepath):
                    if kind == "screenshot":
                        # flush any in-progress text before creating 
                        # block for screenshot
                        if self.current.runs:
                            self.blocks.append(self.current)
                            self.current = Block()
                        self.blocks.append(Block(kind="screenshot", value=filepath))
        # grabs the last block too in case there's no trailing "end"
        if self.current.runs:
            self.blocks.append(self.current)

    def write_docx(self):
        MAX_W = Inches(6)
        MAX_H = Inches(8)

        self.build_blocks()
        doc = Document()

        for block in self.blocks:
            if block.kind == "heading":
                paragraph = doc.add_heading("", level=block.value)
            elif block.kind == "bullet":
                paragraph = doc.add_paragraph(style=block.value)
            elif block.kind == "screenshot":
                pic = doc.add_picture(block.value, width=MAX_W) # value is filepath
                # If height is greater than MAX_H then the height is reduced
                # to the max height and the width is shrinked to match
                if pic.height > MAX_H:
                    ratio = MAX_H / pic.height
                    pic.height = MAX_H
                    pic.width = int(pic.width * ratio)
            else:
                # Just adds words; word pgh is non stop until a heading, bullet, or sct is inserted
                paragraph = doc.add_paragraph()

            for run in block.runs:
                word_run = paragraph.add_run(run.text)
                word_run.italic = run.italic

        doc.save(f"{self.path}/test.docx")



            
    







