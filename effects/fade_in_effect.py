# effects/fade_in_effect.py

import bpy

def apply(text_obj, start_frame, end_frame):
    """
    Animates the text object's opacity to create a fade-in effect.
    """
    # Ensure the text object has a material
    if not text_obj.data.materials:
        material = bpy.data.materials.new(name=f"Material_{text_obj.name}")
        text_obj.data.materials.append(material)
    else:
        material = text_obj.data.materials[0]

    # Enable nodes
    material.use_nodes = True
    nodes = material.node_tree.nodes

    # Remove default nodes
    for node in nodes:
        nodes.remove(node)

    # Create nodes
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    emission_node = nodes.new(type='ShaderNodeEmission')
    transparent_node = nodes.new(type='ShaderNodeBsdfTransparent')
    mix_shader = nodes.new(type='ShaderNodeMixShader')

    # Set up node tree
    material.node_tree.links.new(mix_shader.outputs[0], output_node.inputs[0])
    material.node_tree.links.new(transparent_node.outputs[0], mix_shader.inputs[1])
    material.node_tree.links.new(emission_node.outputs[0], mix_shader.inputs[2])

    # Set emission color
    emission_node.inputs['Color'].default_value = text_obj.data.materials[0].node_tree.nodes['Emission'].inputs['Color'].default_value

    # Animate the 'Fac' of the Mix Shader
    mix_input = mix_shader.inputs['Fac']
    mix_input.default_value = 1  # Start fully transparent

    # Create animation
    mix_input.keyframe_insert(data_path='default_value', frame=start_frame)
    mix_input.default_value = 0  # Fully opaque
    mix_input.keyframe_insert(data_path='default_value', frame=start_frame + 10)  # Fade in over 10 frames
