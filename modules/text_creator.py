# modules/text_creator.py

import bpy
import os
import math
from mathutils import Vector

def create_text_objects(chunks, config):
    """
    Creates text objects in Blender for each chunk of text.
    Returns a list of created text objects.
    """
    text_objects = []

    # Load fonts
    font_path = os.path.join(config['FONT_PATH'], config['DEFAULT_FONT'])
    bold_font_path = os.path.join(config['FONT_PATH'], config['BOLD_FONT'])
    fonts = load_fonts(font_path, bold_font_path)

    # Set scene background color
    set_background_color(config['BACKGROUND_COLOR'])

    # Get camera settings
    camera = bpy.context.scene.camera
    if not camera:
        print("No camera found in the scene. Please add a camera.")
        return text_objects

    # Get camera view size
    if camera.data.type == 'PERSP':
        distance = (Vector((0, 0, 0)) - camera.location).length
        view_width, view_height = get_camera_view_size(camera, distance)
    elif camera.data.type == 'ORTHO':
        view_width, view_height = get_camera_view_size(camera, distance=None)
    else:
        print(f"Unsupported camera type: {camera.data.type}. Defaulting view size to 10x10.")
        view_width, view_height = 10, 10  # Default values

    # Define padding
    padding = config.get('SCALE_PADDING', 0.95)

    for idx, chunk in enumerate(chunks):
        text_content = chunk['text']
        start_time, end_time = chunk['timestamp']

        # Create text object
        bpy.ops.object.text_add()
        text_obj = bpy.context.object
        text_obj.name = f"TextObject_{idx}"
        text_obj.data.body = text_content

        # Set text properties
        set_text_properties(text_obj, config, fonts)

        # Position text object (center)
        text_obj.location = (0, 0, 0)

        # Ensure the origin is centered
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

        # Calculate text dimensions
        width, height, _ = get_text_dimensions(text_obj)

        # Determine scaling factor with padding
        if camera.data.type == 'PERSP':
            scale_x = view_width / width if width > 0 else 1
            scale_y = view_height / height if height > 0 else 1
            scale_factor = min(scale_x, scale_y, 1) * config.get('MAX_SCALE', 1.0) * padding  # Prevent upscaling and add padding
        elif camera.data.type == 'ORTHO':
            aspect_ratio = camera.data.sensor_width / camera.data.sensor_height
            view_width = camera.data.ortho_scale * aspect_ratio
            view_height = camera.data.ortho_scale
            scale_x = view_width / width if width > 0 else 1
            scale_y = view_height / height if height > 0 else 1
            scale_factor = min(scale_x, scale_y, 1) * config.get('MAX_SCALE', 1.0) * padding  # Prevent upscaling and add padding
        else:
            scale_factor = 1  # Default scaling

        # Apply scaling
        text_obj.scale = (scale_factor, scale_factor, scale_factor)

        # Hide text before start_time and after end_time
        frame_start = int(start_time * config['FRAME_RATE'])
        frame_end = int(end_time * config['FRAME_RATE'])

        # Keyframe visibility
        set_visibility_keyframes(text_obj, frame_start, frame_end)

        text_objects.append(text_obj)

    return text_objects

def load_fonts(default_font_path, bold_font_path):
    """
    Loads the fonts and returns a dictionary with font references.
    """
    fonts = {}
    if os.path.isfile(default_font_path):
        fonts['default'] = bpy.data.fonts.load(default_font_path)
    else:
        fonts['default'] = bpy.data.fonts.load('Bfont')
        print(f"Default font not found at {default_font_path}. Using Blender's default font.")

    if os.path.isfile(bold_font_path):
        fonts['bold'] = bpy.data.fonts.load(bold_font_path)
    else:
        fonts['bold'] = fonts['default']
        print(f"Bold font not found at {bold_font_path}. Using default font.")

    return fonts

def set_text_properties(text_obj, config, fonts):
    """
    Sets the properties of the text object.
    """
    text_obj.data.font = fonts['default']
    text_obj.data.size = config['TEXT_SIZE']
    text_obj.data.align_x = 'CENTER'
    text_obj.data.align_y = 'CENTER'

    # Set text color using an Emission shader
    material = bpy.data.materials.new(name=f"Material_{text_obj.name}")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Clear default nodes
    for node in nodes:
        nodes.remove(node)

    # Create shader nodes
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    emission_node = nodes.new(type='ShaderNodeEmission')

    # Set emission color to the desired text color
    emission_node.inputs['Color'].default_value = config['TEXT_COLOR']

    # Link the Emission shader to the Material Output
    links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])

    # Assign the material to the text object
    text_obj.data.materials.append(material)

def set_visibility_keyframes(text_obj, frame_start, frame_end):
    """
    Sets keyframes to control the visibility of the text object.
    """
    # Ensure the object has animation data
    if not text_obj.animation_data:
        text_obj.animation_data_create()
    action = text_obj.animation_data.action
    if not action:
        action = bpy.data.actions.new(name=f"Action_{text_obj.name}")
        text_obj.animation_data.action = action

    # Animate the 'hide_viewport' and 'hide_render' properties
    for fcurve_name in ['hide_viewport', 'hide_render']:
        # Check if fcurve already exists to avoid duplication
        existing_fcurves = [fc for fc in action.fcurves if fc.data_path == fcurve_name]
        if existing_fcurves:
            fcurve = existing_fcurves[0]
        else:
            fcurve = action.fcurves.new(data_path=fcurve_name)

        # Insert keyframes with padding
        keyframes = [
            (frame_start - 1, 1),
            (frame_start, 0),
            (frame_end, 0),
            (frame_end + 1, 1)
        ]

        for frame, value in keyframes:
            keyframe = fcurve.keyframe_points.insert(frame=frame, value=value)
            keyframe.interpolation = 'CONSTANT'

def set_background_color(color):
    """
    Sets the background color of the scene.
    """
    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    background_node = nodes.get('Background')
    if background_node is None:
        background_node = nodes.new(type='ShaderNodeBackground')
    background_node.inputs['Color'].default_value = color

def get_text_dimensions(text_obj):
    """
    Returns the dimensions of the text object.
    """
    bpy.context.view_layer.update()  # Ensure up-to-date dimensions
    return text_obj.dimensions.x, text_obj.dimensions.y, text_obj.dimensions.z

def get_camera_view_size(camera, distance):
    """
    Calculates the view width and height at a certain distance from the camera.
    Supports both perspective and orthographic cameras.
    """
    if camera.data.type == 'PERSP':
        fov = camera.data.angle  # Vertical field of view in radians
        aspect_ratio = camera.data.sensor_width / camera.data.sensor_height
        height = 2 * distance * math.tan(fov / 2)
        width = height * aspect_ratio
    elif camera.data.type == 'ORTHO':
        ortho_scale = camera.data.ortho_scale
        aspect_ratio = camera.data.sensor_width / camera.data.sensor_height
        height = ortho_scale
        width = height * aspect_ratio
    else:
        print(f"Unsupported camera type: {camera.data.type}. Defaulting view size to 10x10.")
        width, height = 10, 10  # Default values
    return width, height
