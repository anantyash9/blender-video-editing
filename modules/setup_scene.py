# modules/setup_scene.py

import bpy

def clear_scene():
    """
    Removes all objects from the scene.
    """
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    # Remove all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    # Remove all meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    #Remove all cameras
    for camera in bpy.data.cameras:
        bpy.data.cameras.remove(camera)
    # Remove all lights
    for light in bpy.data.lights:
        bpy.data.lights.remove(light)
def remove_default_cube():
    """
    Removes the default cube from the scene.
    """
    bpy.data.objects.remove(bpy.data.objects['Cube'], do_unlink=True)
    #print camera properties before removing
    print(bpy.data.objects['Camera'].data.lens)

    #remove default camera
    bpy.data.objects.remove(bpy.data.objects['Camera'], do_unlink=True)
def setup_camera(config):
    """
    Sets up the camera in the scene.
    """
    # Add a camera
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "Camera"

    # Set camera location and rotation
    camera.location = (0,0, config['CAMERA_DISTANCE'])
    # camera.rotation_euler = (0, 1.50, 0)  # Rotate 90 degrees to face the text
    #point the camera to 0,0,0
    camera.rotation_euler = (0, 0, 0)

    # Adjust rotation if needed
    # camera.rotation_euler = (1.5708, 0, 3.1416)  # Uncomment if text is not visible

    # Set camera properties if needed
    camera.data.lens = config.get('CAMERA_FOCAL_LENGTH', 50)
    camera.data.ortho_scale = config.get('CAMERA_ORTHO_SCALE', 5)
    #set the camera viewport ratio to portrait based on the resolution in the config file
    camera.data.sensor_fit = 'VERTICAL'
    #set the scene resolution
    bpy.context.scene.render.resolution_x = config['RESOLUTION'][0]
    bpy.context.scene.render.resolution_y = config['RESOLUTION'][1]
    #set camera sensor size to the resolution in the config file
    camera.data.sensor_width = config['RESOLUTION'][0]
    camera.data.sensor_height = config['RESOLUTION'][1]
    #camera orthographic 
    camera.data.type = 'ORTHO'


    # Set the camera as the active camera
    bpy.context.scene.camera = camera

def setup_lighting():
    """
    Sets up basic lighting in the scene.
    """
    # Add a light source
    bpy.ops.object.light_add(type='SUN')
    light = bpy.context.object
    light.name = "SunLight"
    light.location = (0, 0, 10)
    light.rotation_euler = (0, 0, 0)
    light.data.energy = 5  # Adjust as needed

def setup_world_background(color):
    """
    Sets the world background color.
    """
    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    background_node = nodes.get('Background')
    if background_node is None:
        background_node = nodes.new(type='ShaderNodeBackground')
    background_node.inputs['Color'].default_value = color

def setup_scene(config):
    """
    Calls all the setup functions to prepare the scene.
    """
    remove_default_cube()
    # clear_scene()
    setup_camera(config)
    # setup_lighting()
    # setup_world_background(config['BACKGROUND_COLOR'])
    # remove_default_cube()
