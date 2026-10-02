import json
import os
from pathlib import Path

# The settings file lives in AppData so we can always write to it on work computers
SETTINGS_DIR = Path(os.getenv("APPDATA", Path.home())) / "Documentation Automater"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


def load_settings():
    # Read the JSON file. If it's missing or messed up, just start with an empty dict
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_settings(settings):
    # Make the settings folder if it isn't there yet, then write everything back out
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)


def get_root_folder():
    # Returns the root Projects folder as a Path, or None if we don't have one yet
    root = load_settings().get("root_folder")
    # If the saved folder got deleted, treat it like there's no root folder
    if root and Path(root).is_dir():
        return Path(root)
    return None


def set_root_folder(path):
    # Load the current settings so we don't wipe out anything else, then update root_folder
    settings = load_settings()
    settings["root_folder"] = str(path)
    save_settings(settings)