# modules/effect_manager.py

import importlib
import sys
import os

def load_effects(effect_names):
    """
    Dynamically imports effect modules based on the provided list.
    Returns a list of effect modules.
    """
    effects = []
    for effect_name in effect_names:
        try:
            module = importlib.import_module(effect_name)
            effects.append(module)
        except ModuleNotFoundError:
            print(f"Effect module '{effect_name}' not found.")
    return effects

def apply_effects(text_obj, effects_list, start_frame, end_frame):
    """
    Applies each effect in the effects_list to the text_obj.
    """
    for effect in effects_list:
        if hasattr(effect, 'apply'):
            effect.apply(text_obj, start_frame, end_frame)
        else:
            print(f"Effect module '{effect.__name__}' does not have an 'apply' function.")
