"""

This test takes a merged dictionary (created from words dictionary and button_history dictionary)
and converts text and effect commands into a word document. It does NOT SUPPORT IMAGES yet.

Merged dictionary comes from TWO separate dictionaries/lists:
  - `words`   - from faster-whisper: {word, start_time, end_time}
  - `buttons` - from the recorder: {button_type, click_time, start/stop}

"""

from dataclasses import dataclass, field
from docx import Document


# ---------------------------------------------------------------------------
# STEP 1: data shapes
#
# dataclass just auto generates __init__ etc for a class that only holds
# fields. Run("Save", italic=True) makes an object with .text and .italic.
# the "= False" stuff are defaults so you don't have to pass every field.
# ---------------------------------------------------------------------------

@dataclass
class Run:
    """chunk of text that all shares the same bold/italic."""
    text: str
    bold: bool = False
    italic: bool = False


@dataclass
class Block:
    """one paragraph/heading/bullet. ends on enter."""
    kind: str = "paragraph"   # "paragraph", "heading", or "bullet"
    level: int = 1            # heading level, ignored for paragraph/bullet
    # default_factory=list so each Block gets its own list.
    # runs: list = [] would share the SAME list across every Block (classic python gotcha)
    runs: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# STEP 2: fake data, standing in for what would actually come out of the
# match/merge step on real words + button_history.
#
#
# Events[] list is the merged list that holds both word[] and button_history[] dict
# values. Each event in the list is (timestamp_in_seconds, event_type, value)
#   - Rows with kind == "word" stand in for entries from words[] dict
#     (word + timestamp)
#   - All other rows (heading, bullet, italic_on/off, bold_on/off, enter)
#     stand in for entries from buttons[] dict (button type + click
#     timestamp)
#
# Create the merged list with something like this:
#   events = sorted(words_as_events + buttons_as_events, key=lambda e: e[0])
# ---------------------------------------------------------------------------

events = [
    (0.0,  "heading",     1),             # heading 1 block
    (0.5,  "word",        "Logging"),
    (0.9,  "word",        "into"),
    (1.2,  "word",        "the"),
    (1.5,  "word",        "portal"),
    (2.0,  "enter",       None),          # closes the heading block

    (2.5,  "word",        "Open"),
    (2.9,  "word",        "your"),
    (3.2,  "word",        "browser"),
    (3.6,  "word",        "and"),
    (3.9,  "word",        "click"),
    (4.2,  "italic_on",   None),
    (4.3,  "word",        "Sign"),
    (4.6,  "word",        "In"),
    (4.9,  "italic_off",  None),
    (5.2,  "word",        "at"),
    (5.5,  "word",        "the"),
    (5.8,  "word",        "top."),
    (6.3,  "enter",       None),          # closes the paragraph

    (6.8,  "bullet",      None),          # bullet block
    (7.0,  "bold_on",     None),
    (7.1,  "word",        "Never"),
    (7.4,  "bold_off",    None),
    (7.7,  "word",        "share"),
    (8.0,  "word",        "your"),
    (8.3,  "word",        "password."),
    (8.8,  "enter",       None),
]


# ---------------------------------------------------------------------------
# STEP 3: loop through events in time order, building blocks/runs as we go
#
# current = the block being built right now
# bold/italic = whether those styles are currently on
# ---------------------------------------------------------------------------

def build_blocks(events):
    blocks = []
    current = Block()
    bold = False
    italic = False

    # sort just in case events come in slightly out of order
    # e[0] is the timestamp, so this sorts by time
    for timestamp, kind, value in sorted(events, key=lambda e: e[0]):

        if kind == "word":
            # from the words dict
            # if the last run already matches the current bold/italic state,
            # tack the word onto it instead of making a new run. this keeps
            # "Sign In" as ONE italic run instead of two
            last = current.runs[-1] if current.runs else None
            if last and last.bold == bold and last.italic == italic:
                last.text += " " + value
            else:
                text = (" " if current.runs else "") + value  # no leading space on first word
                current.runs.append(Run(text, bold=bold, italic=italic))

        # everything below here comes from the buttons dict.
        # bold/italic on/off just flip a flag, they don't touch the block directly
        elif kind == "bold_on":
            bold = True
        elif kind == "bold_off":
            bold = False
        elif kind == "italic_on":
            italic = True
        elif kind == "italic_off":
            italic = False

        elif kind == "heading":
            # just changes what type the current block is
            # nothing needs closing, enter ends the block for us either way
            current.kind = "heading"
            current.level = value
        elif kind == "bullet":
            current.kind = "bullet"

        elif kind == "enter":
            # enter is a button event too, same as bold/italic, it just ends
            # the block instead of toggling a style
            blocks.append(current)
            current = Block()

    # grab the last block too in case there's no trailing enter
    if current.runs:
        blocks.append(current)

    return blocks


# ---------------------------------------------------------------------------
# STEP 4: blocks -> actual docx file
# ---------------------------------------------------------------------------

def write_docx(blocks, path):
    doc = Document()

    for block in blocks:
        if block.kind == "heading":
            # uses word's built in heading styles, text gets added as runs below
            paragraph = doc.add_heading("", level=block.level)
        elif block.kind == "bullet":
            paragraph = doc.add_paragraph(style="List Bullet")
        else:
            paragraph = doc.add_paragraph()

        for run in block.runs:
            word_run = paragraph.add_run(run.text)
            word_run.bold = run.bold
            word_run.italic = run.italic

    doc.save(path)

if __name__ == "__main__":
    blocks = build_blocks(events)

    for b in blocks:
        print(b)  # dataclass prints its own fields automatically

    write_docx(blocks, "sop_demo.docx")
    print("\nWrote sop_demo.docx")