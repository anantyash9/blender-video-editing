# modules/renderer.py

import bpy
import os

def setup_rendering(config):
    """
    Sets up rendering parameters based on the configuration.
    """
    scene = bpy.context.scene
    scene.name = config.get('SCENE_NAME', 'Scene')

    # Set render engine to Eevee
    scene.render.engine = 'BLENDER_EEVEE_NEXT'

    # Set resolution
    scene.render.resolution_x = config['RESOLUTION'][0]
    scene.render.resolution_y = config['RESOLUTION'][1]
    scene.render.resolution_percentage = 100

    # Set frame rate
    scene.render.fps = config['FRAME_RATE']

    # Set output path
    output_dir = os.path.dirname(config['OUTPUT_PATH'])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    scene.render.filepath = config['OUTPUT_PATH']

    # Set output format
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.ffmpeg.audio_codec = 'AAC'
    scene.render.ffmpeg.audio_bitrate = 192

    # For Eevee, GPU rendering is used by default
    print("Eevee uses GPU rendering by default. No additional configuration required.")

def render_animation():
    """
    Initiates the rendering process.
    """
    print("Output saved to:", bpy.context.scene.render.filepath)
    bpy.ops.render.render(animation=True)
    print("Rendering animation...")
    

