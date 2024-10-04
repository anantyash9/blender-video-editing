# modules/visual_elements_manager.py

import bpy
import os
import bpy

import bpy

def create_fullscreen_plane(z_location, name):
    """
    Creates a background plane that matches the orthographic camera viewport size
    and places it at (0, 0, -1).
    """
    # Get the current scene and camera
    scene = bpy.context.scene
    camera = scene.camera

    # Ensure the camera is orthographic
    if camera.data.type != 'ORTHO':
        print("Camera is not orthographic. Please use an orthographic camera.")
        return None

    # Get the orthographic scale of the camera (this represents half of the viewport height)
    ortho_scale = camera.data.ortho_scale

    # Get the aspect ratio (width/height) of the scene's resolution
    render = scene.render
    resolution_x = render.resolution_x
    resolution_y = render.resolution_y

    # Take into account the pixel aspect ratio
    pixel_aspect_ratio = render.pixel_aspect_x / render.pixel_aspect_y

    # Calculate the correct plane size
    # ortho_scale is half the height, so we multiply by 2 for full height
    plane_height = 2 * ortho_scale
    plane_width = plane_height * (resolution_x / resolution_y) * pixel_aspect_ratio

    # Create the background plane
    bpy.ops.mesh.primitive_plane_add(size=2)
    plane = bpy.context.object
    plane.name = name

    # Scale the plane to match the camera's viewport size
    plane.scale = (plane_width / 4, plane_height / 4, 1)

    # Set the location of the plane (0, 0, -1)
    plane.location = (0, 0, z_location)

    #apply scale position and rotation
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    return plane



def add_visual_elements(visual_elements, config):
    """
    Adds visual elements to the scene based on the visual_elements list.
    """
    for element in visual_elements:
        file_path = element['file_path']
        element_type = element['type']
        timestamp = element['timestamp']
        media = element['media']
        effects = element.get('effects', [])

        # Ensure the file exists
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue

        # Add the visual element
        obj = add_visual_element(file_path, element_type, timestamp, media, effects, config)

def add_visual_element(file_path, element_type, timestamp, media, effects, config):
    """
    Adds a single visual element to the scene.
    """
    start_time, end_time = timestamp
    start_frame = int(start_time * config['FRAME_RATE'])
    end_frame = int(end_time * config['FRAME_RATE'])

    # Create a plane for the visual element
    name = f"{element_type.capitalize()}_{os.path.basename(file_path)}"
    
    if element_type == 'background':
        plane = create_fullscreen_plane(z_location=-1, name=name)
    elif element_type == 'overlay':
        plane = create_fullscreen_plane(z_location=1, name=name)
    elif element_type == 'main':
        plane = create_fullscreen_plane(z_location=0, name=name)
    else:
        print(f"Unknown element type: {element_type}")
        return None
    # chech if its a video or image
    if media == 'video':
        material = create_material_with_chroma_key_media(file_path, plane)
        if not material:
            return None
    else:
        # Load the media as a texture and assign it to the material
        material = create_material_with_media(file_path, media, plane)
        if not material:
            return None

    # Hide the plane outside of its active time
    set_visibility_keyframes(plane, start_frame, end_frame)

    # Apply effects if any
    apply_effects(plane, effects, start_frame, end_frame, element_type)

    return plane



def create_material_with_media(file_path, media, plane):
    """
    Creates and assigns a material with a texture based on the provided media file.
    Maintains aspect ratio and ensures the texture fits the plane's height.
    """
    material = bpy.data.materials.new(name=f"{plane.name}_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create necessary nodes
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    emission_node = nodes.new(type='ShaderNodeEmission')
    texture_node = nodes.new(type='ShaderNodeTexImage')  # Create the texture node
    mapping_node = nodes.new(type='ShaderNodeMapping')
    coord_node = nodes.new(type='ShaderNodeTexCoord')

    # Set up the node tree connections
    links.new(coord_node.outputs['UV'], mapping_node.inputs['Vector'])
    links.new(mapping_node.outputs['Vector'], texture_node.inputs['Vector'])
    links.new(texture_node.outputs['Color'], emission_node.inputs['Color'])
    links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])

    # Load the image or video into the texture node
    try:
        image = bpy.data.images.load(file_path)
    except Exception as e:
        print(f"Failed to load media file {file_path}: {e}")
        return None

    # Ensure that the texture fits the height of the plane and maintains aspect ratio
    if media == 'image' or media == 'video':
        image_width, image_height = image.size[:2]

        # Get plane dimensions since the scale may have been adjusted   
        plane_x_dim = plane.dimensions.x
        plane_y_dim = plane.dimensions.y

        # Calculate the aspect ratios
        image_aspect = image_width / image_height
        plane_aspect = plane_x_dim / plane_y_dim

        # Adjust the UV scaling to fit the height of the plane and maintain the image's aspect ratio
        if image_aspect > plane_aspect:
            # Image is wider relative to the plane, so scale UV in X direction (crop sides)
            uv_scale_x = plane_aspect/image_aspect
            uv_scale_y = 1
            x_location = (1 - uv_scale_x) / 2
            y_location = 0
        else:
            # Image is taller relative to the plane, so scale UV in Y direction (no cropping needed)
            uv_scale_x = 1
            uv_scale_y = image_aspect/plane_aspect
            x_location = 0
            y_location = (1 - uv_scale_y) / 2

        # Apply the UV scale to the mapping node
        mapping_node.inputs['Scale'].default_value = (uv_scale_x, uv_scale_y, 1)
        # Center the UV mapping
        mapping_node.inputs['Location'].default_value = (x_location, y_location, 0)


    # Assign the appropriate image or video to the texture node
    if media == 'image':
        texture_node.image = image
    elif media == 'video':
        image.source = 'MOVIE'
        texture_node.image = image
    else:
        print(f"Unsupported media type: {media}")
        return None

    # Assign the material to the plane
    plane.data.materials.append(material)
    
    return material

def create_material_with_chroma_key_media(file_path, plane, key_color=(0, 1, 0), threshold=0.8):
    """
    Creates and assigns a material with chroma keying based on the provided video file.
    Removes the key color (default green) and makes it transparent.
    """
    import bpy

    # Create a new material
    material = bpy.data.materials.new(name=f"{plane.name}_ChromaKey_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create necessary nodes
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    transparent_node = nodes.new(type='ShaderNodeBsdfTransparent')
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    texture_node = nodes.new(type='ShaderNodeTexImage')
    mapping_node = nodes.new(type='ShaderNodeMapping')
    coord_node = nodes.new(type='ShaderNodeTexCoord')
    key_color_node = nodes.new(type='ShaderNodeRGB')
    subtract_node = nodes.new(type='ShaderNodeVectorMath')
    length_node = nodes.new(type='ShaderNodeVectorMath')
    threshold_node = nodes.new(type='ShaderNodeMath')
    mix_shader_node = nodes.new(type='ShaderNodeMixShader')

    # Set node properties
    key_color_node.outputs['Color'].default_value = (*key_color, 1)
    subtract_node.operation = 'SUBTRACT'
    length_node.operation = 'LENGTH'
    threshold_node.operation = 'GREATER_THAN'
    threshold_node.inputs[1].default_value = threshold

    # Set material blend mode to allow transparency
    # material.blend_method = 'BLEND'
    # material.shadow_method = 'NONE'

    # Set up the node tree connections
    links.new(coord_node.outputs['UV'], mapping_node.inputs['Vector'])
    links.new(mapping_node.outputs['Vector'], texture_node.inputs['Vector'])
    links.new(texture_node.outputs['Color'], principled_node.inputs['Base Color'])
    links.new(texture_node.outputs['Color'], subtract_node.inputs[0])
    links.new(key_color_node.outputs['Color'], subtract_node.inputs[1])
    links.new(subtract_node.outputs['Vector'], length_node.inputs[0])
    links.new(length_node.outputs['Value'], threshold_node.inputs[0])
    links.new(threshold_node.outputs['Value'], mix_shader_node.inputs['Fac'])
    links.new(transparent_node.outputs['BSDF'], mix_shader_node.inputs[1])
    links.new(principled_node.outputs['BSDF'], mix_shader_node.inputs[2])
    links.new(mix_shader_node.outputs['Shader'], output_node.inputs['Surface'])

    # Load the video into the texture node
    try:
        image = bpy.data.images.load(file_path)
        image.source = 'MOVIE'
        texture_node.image = image
        texture_node.image_user.frame_duration = image.frame_duration
        #auto refresh the image
        texture_node.image_user.use_auto_refresh = True
        texture_node.projection = 'BOX'
        #extention to extend the video to all frames
        texture_node.extension = 'EXTEND'


        # set the number of frames for the video to all frames in the video
    except Exception as e:
        print(f"Failed to load media file {file_path}: {e}")
        return None

    # Adjust UV mapping to maintain aspect ratio
    image_width, image_height = image.size[:2]
    plane_x_dim = plane.dimensions.x
    plane_y_dim = plane.dimensions.y
    image_aspect = image_width / image_height
    plane_aspect = plane_x_dim / plane_y_dim

    if image_aspect > plane_aspect:
        uv_scale_x = plane_aspect / image_aspect
        uv_scale_y = 1
        x_location = (1 - uv_scale_x) / 2
        y_location = 0.94
    else:
        uv_scale_x = 1
        uv_scale_y = image_aspect / plane_aspect
        x_location = 0
        y_location = (1 - uv_scale_y) / 2

    mapping_node.inputs['Scale'].default_value = (uv_scale_x, uv_scale_y, 1)
    mapping_node.inputs['Location'].default_value = (x_location, y_location, 0)
    #rotate the video -90 degrees
    mapping_node.inputs['Rotation'].default_value = (0, 0, -1.5708)

    # Assign the material to the plane
    plane.data.materials.append(material)

    return material


def set_visibility_keyframes(obj, frame_start, frame_end):
    """
    Sets keyframes to control the visibility of the object.
    """
    obj.hide_viewport = True
    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_viewport", frame=frame_start - 1)
    obj.keyframe_insert(data_path="hide_render", frame=frame_start - 1)

    obj.hide_viewport = False
    obj.hide_render = False
    obj.keyframe_insert(data_path="hide_viewport", frame=frame_start)
    obj.keyframe_insert(data_path="hide_render", frame=frame_start)

    obj.keyframe_insert(data_path="hide_viewport", frame=frame_end)
    obj.keyframe_insert(data_path="hide_render", frame=frame_end)

    obj.hide_viewport = True
    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_viewport", frame=frame_end + 1)
    obj.keyframe_insert(data_path="hide_render", frame=frame_end + 1)

def apply_effects(obj, effects, start_frame, end_frame, element_type):
    """
    Applies effects to the visual element.
    """
    for effect in effects:
        if effect == 'pan_and_zoom':
            pan_and_zoom_effect(obj, start_frame, end_frame, element_type)
        elif effect == 'zoom_in':
            zoom_effect(obj, start_frame, end_frame, zoom_in=True, element_type=element_type)
        elif effect == 'zoom_out':
            zoom_effect(obj, start_frame, end_frame, zoom_in=False, element_type=element_type)
        elif effect == 'corner_to_corner_pan':
            corner_to_corner_pan_effect(obj, start_frame, end_frame, element_type)
        else:
            print(f"Unknown effect: {effect}")
def pan_and_zoom_effect(obj, start_frame, end_frame, element_type):
    """
    Applies a pan and zoom effect to the object.
    """
    # Access the mapping node
    material = obj.data.materials[0]
    mapping_node = material.node_tree.nodes.get('Mapping')

    if not mapping_node:
        print("Mapping node not found in material.")
        return

    # Initial mapping settings
    mapping_node.inputs['Location'].default_value = (0, 0, 0)
    mapping_node.inputs['Scale'].default_value = (1, 1, 1)
    mapping_node.inputs['Location'].keyframe_insert(data_path='default_value', frame=start_frame)
    mapping_node.inputs['Scale'].keyframe_insert(data_path='default_value', frame=start_frame)

    # Final mapping settings
    if element_type == 'background':
        # For backgrounds, we can pan horizontally and zoom slightly
        mapping_node.inputs['Location'].default_value = (0.1, 0, 0)  # Pan right
        mapping_node.inputs['Scale'].default_value = (0.9, 0.9, 1)   # Zoom in
    elif element_type == 'overlay':
        # For overlays, the plane should not move; apply pan and zoom to the texture
        mapping_node.inputs['Location'].default_value = (-0.1, 0, 0)  # Pan left
        mapping_node.inputs['Scale'].default_value = (1.1, 1.1, 1)    # Zoom out
    mapping_node.inputs['Location'].keyframe_insert(data_path='default_value', frame=end_frame)
    mapping_node.inputs['Scale'].keyframe_insert(data_path='default_value', frame=end_frame)

import random

def zoom_effect(obj, start_frame, end_frame, zoom_in=True, element_type='background'):
    """
    Applies a zoom in and revert back to original size effect multiple times between start and end frame.
    The zoom in and zoom out happen quickly (0.5 sec), and the zoomed state is held for 4-6 seconds before reverting.
    The waiting time between zoom-ins and zoom-outs is randomized between 4 and 6 seconds.

    :param obj: The object to apply the zoom effect to.
    :param start_frame: The frame at which the zoom effect starts.
    :param end_frame: The frame at which the zoom effect ends.
    :param zoom_in: If True, applies a zoom-in effect; otherwise, applies zoom-out.
    :param element_type: Defines the element type (background/overlay etc.)
    """
    import random

    material = obj.data.materials[0]
    mapping_node = material.node_tree.nodes.get('Mapping')

    if not mapping_node:
        print("Mapping node not found in material.")
        return

    # Calculate FPS
    fps = bpy.context.scene.render.fps

    # Initial and zoomed-in scale calculations
    initial_scale = mapping_node.inputs['Scale'].default_value.copy()
    initial_scale=(initial_scale[0], initial_scale[1], initial_scale[2])
    initial_location = mapping_node.inputs['Location'].default_value.copy()
    initial_location=(initial_location[0], initial_location[1], initial_location[2])
    zoom_in_percentage = 0.9  # Define how much to zoom in
    zoom_scale = (
        initial_scale[0] * zoom_in_percentage,
        initial_scale[1] * zoom_in_percentage,
        1
    )
    zoom_location = (initial_location[0], 0.88, initial_location[2])

    current_frame = start_frame

    # Set the initial scale and location at the start_frame
    mapping_node.inputs['Scale'].default_value = initial_scale
    mapping_node.inputs['Scale'].keyframe_insert(data_path='default_value', frame=start_frame)
    mapping_node.inputs['Location'].default_value = initial_location
    mapping_node.inputs['Location'].keyframe_insert(data_path='default_value', frame=start_frame)

    # Loop through and apply the effect until the end frame is reached
    while current_frame < end_frame:
        # Random wait time before zoom (4 to 6 seconds)
        wait_time_before_zoom = random.uniform(4, 6)
        wait_frames_before_zoom = wait_time_before_zoom * fps

        # Calculate the frame when zoom in starts
        zoom_in_start_frame = current_frame + wait_frames_before_zoom

        # Check if there's enough time left for a full zoom cycle
        total_zoom_cycle_frames = (0.5 + random.uniform(4, 6) + 0.5) * fps  # zoom in + hold + zoom out
        if zoom_in_start_frame + total_zoom_cycle_frames > end_frame:
            # Not enough time for another cycle, exit loop
            break

        # Hold initial scale until zoom_in_start_frame
        mapping_node.inputs['Scale'].default_value = initial_scale
        mapping_node.inputs['Scale'].keyframe_insert(data_path='default_value', frame=zoom_in_start_frame - 1)
        mapping_node.inputs['Location'].default_value = initial_location
        mapping_node.inputs['Location'].keyframe_insert(data_path='default_value', frame=zoom_in_start_frame - 1)

        # Zoom in over 0.5 seconds
        zoom_in_end_frame = zoom_in_start_frame + (0.5 * fps)
        mapping_node.inputs['Scale'].default_value = zoom_scale
        mapping_node.inputs['Scale'].keyframe_insert(data_path='default_value', frame=zoom_in_end_frame)
        mapping_node.inputs['Location'].default_value = zoom_location
        mapping_node.inputs['Location'].keyframe_insert(data_path='default_value', frame=zoom_in_end_frame)

        # Hold zoomed state for 4-6 seconds
        hold_time = random.uniform(4, 6)
        hold_frames = hold_time * fps
        hold_end_frame = zoom_in_end_frame + hold_frames

        mapping_node.inputs['Scale'].default_value = zoom_scale
        mapping_node.inputs['Scale'].keyframe_insert(data_path='default_value', frame=hold_end_frame)
        mapping_node.inputs['Location'].default_value = zoom_location
        mapping_node.inputs['Location'].keyframe_insert(data_path='default_value', frame=hold_end_frame)

        # Zoom out over 0.5 seconds
        zoom_out_end_frame = hold_end_frame + (0.5 * fps)
        mapping_node.inputs['Scale'].default_value = initial_scale
        mapping_node.inputs['Scale'].keyframe_insert(data_path='default_value', frame=zoom_out_end_frame)
        mapping_node.inputs['Location'].default_value = initial_location
        mapping_node.inputs['Location'].keyframe_insert(data_path='default_value', frame=zoom_out_end_frame)

        # Update current_frame to the end of this cycle
        current_frame = zoom_out_end_frame

    # After the loop, ensure the object stays at initial scale till end_frame
    mapping_node.inputs['Scale'].default_value = initial_scale
    mapping_node.inputs['Scale'].keyframe_insert(data_path='default_value', frame=end_frame)
    mapping_node.inputs['Location'].default_value = initial_location
    mapping_node.inputs['Location'].keyframe_insert(data_path='default_value', frame=end_frame)

    print("Zoom effect completed.")



def corner_to_corner_pan_effect(obj, start_frame, end_frame, element_type):
    """
    Pans the texture from one corner to the opposite corner.
    """
    material = obj.data.materials[0]
    mapping_node = material.node_tree.nodes.get('Mapping')

    if not mapping_node:
        print("Mapping node not found in material.")
        return

    # Initial location
    mapping_node.inputs['Location'].default_value = (-0.1, -0.1, 0)
    mapping_node.inputs['Location'].keyframe_insert(data_path='default_value', frame=start_frame)

    # Final location
    mapping_node.inputs['Location'].default_value = (0.1, 0.1, 0)
    mapping_node.inputs['Location'].keyframe_insert(data_path='default_value', frame=end_frame)

