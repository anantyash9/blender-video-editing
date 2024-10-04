# main.py

import bpy
import sys
import os

# print blender version
print(bpy.app.version_string)

# Adjust the path to ensure modules and effects can be imported
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, 'modules'))
sys.path.append(os.path.join(script_dir, 'effects'))

from config import CONFIG
from modules import parser, text_creator, effect_manager, renderer, setup_scene, visual_elements_manager

def main():
    # Step 1: Load configurations
    config = CONFIG
    setup_scene.setup_scene(config)

    visual_elements_file = os.path.join(script_dir,'visual_elements.json')
    visual_elements = parser.parse_visual_elements(visual_elements_file)
    if visual_elements:
        # Step 1.3: Add visual elements to the scene
        visual_elements_manager.add_visual_elements(visual_elements, config)
    else:
        print("No visual elements to add.")

    # Step 2: Parse data
    data_file = os.path.join(script_dir, 'transcript.json')
    chunks = parser.parse_data(data_file)

    if not chunks:
        print("No data to process.")
        return

    # Step 3: Create text objects
    text_objects = text_creator.create_text_objects(chunks, config)

    if not text_objects:
        print("No text objects created.")
        return

    # Step 4: Load and apply effects
    effects_list = effect_manager.load_effects(config['EFFECTS'])

    if not effects_list:
        print("No effects to apply.")
    else:
        for text_obj, chunk in zip(text_objects, chunks):
            start_frame = int(chunk['timestamp'][0] * config['FRAME_RATE'])
            end_frame = int(chunk['timestamp'][1] * config['FRAME_RATE'])
            effect_manager.apply_effects(text_obj, effects_list, start_frame, end_frame)

    #set number of frames for the animation
    bpy.context.scene.frame_end = int(chunks[-1]['timestamp'][1] * config['FRAME_RATE'])
    #add audio file to the scene
    bpy.context.scene.frame_end=150
    bpy.context.preferences.filepaths.use_file_compression = False
    #save the blend file
    bpy.ops.wm.save_as_mainfile(filepath='output.blend')

    # Step 5: Set up rendering
    renderer.setup_rendering(config)

    # Step 6: Render the animation
    renderer.render_animation()

if __name__ == "__main__":
    main()
    #use ffmpeg to add audio to the video. the video is saved as output/video.mp4 and the audio is modi.mp3
    # os.system('ffmpeg -i output/video.mp4 -i modi.mp3 -c:v copy -c:a aac -strict experimental output/final.mp4')
