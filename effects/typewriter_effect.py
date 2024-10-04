# effects/typewriter_effect.py

import bpy

def apply(text_obj, start_frame, end_frame):
    """
    Creates a typewriter effect by updating the text content on each frame.
    """
    text = text_obj.data.body
    total_chars = len(text)
    frame_duration = end_frame - start_frame

    if total_chars == 0 or frame_duration == 0:
        return  # Nothing to animate

    frames_per_char = max(1, frame_duration // total_chars)

    # Store the data we need in a custom property on the text object
    text_obj["typewriter_data"] = {
        "full_text": text,
        "start_frame": start_frame,
        "frames_per_char": frames_per_char,
        "end_frame": end_frame
    }

    # Define the frame change handler
    def typewriter_handler(scene):
        current_frame = scene.frame_current
        obj = text_obj
        if "typewriter_data" in obj:
            data = obj["typewriter_data"]
            start = data["start_frame"]
            end = data["end_frame"]
            frames_per_char = data["frames_per_char"]
            full_text = data["full_text"]
            total_chars = len(full_text)

            if current_frame < start:
                obj.data.body = ""
            elif current_frame <= end:
                chars_to_show = min(
                    (current_frame - start) // frames_per_char + 1,
                    total_chars
                )
                obj.data.body = full_text[:chars_to_show]
            else:
                obj.data.body = full_text  # Show full text after end_frame

            # Remove handler after the effect is done
            if current_frame > end:
                bpy.app.handlers.frame_change_post.remove(typewriter_handler)
                del obj["typewriter_data"]

    # Remove existing handlers added by this script
    for handler in bpy.app.handlers.frame_change_post:
        if hasattr(handler, '__name__') and handler.__name__ == "typewriter_handler":
            bpy.app.handlers.frame_change_post.remove(handler)

    # Register the handler
    bpy.app.handlers.frame_change_post.append(typewriter_handler)
