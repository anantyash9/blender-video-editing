# effects/bold_effect.py

import bpy
import os

def apply(text_obj, start_frame, end_frame):
    """
    Applies a bold font to the text object.
    """
    # Assume the bold font is already loaded in text_creator.py and stored in the object's font
    # Change the font to bold
    bold_font = None
    for font in bpy.data.fonts:
        if 'Bold' in font.name:
            bold_font = font
            break

    if bold_font:
        text_obj.data.font = bold_font
    else:
        print("Bold font not found. Using default font.")
