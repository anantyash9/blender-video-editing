import json
import effects  # This imports the effects package
with open('data.json', 'r') as f:
    data = json.load(f)

text = data['text']
chunks = data['chunks']

for chunk in chunks:
    text_content = chunk['text']
    start_time, end_time = chunk['timestamp']
    
    # Create text object
    bpy.ops.object.text_add()
    text_obj = bpy.context.object
    text_obj.data.body = text_content
    
    # Position text object in time
    text_obj.animation_data_create()
    text_obj.animation_data.action = bpy.data.actions.new(name="TextAction")
    fcurve = text_obj.animation_data.action.fcurves.new(data_path="hide_viewport")
    
    # Hide text before start_time
    kf = fcurve.keyframe_points.insert(frame=start_time * fps - 1, value=1)
    # Show text at start_time
    kf = fcurve.keyframe_points.insert(frame=start_time * fps, value=0)
    # Hide text after end_time
    kf = fcurve.keyframe_points.insert(frame=end_time * fps, value=0)
    kf = fcurve.keyframe_points.insert(frame=end_time * fps + 1, value=1)


    # List of effects to apply, can be loaded from a config file or user input
    selected_effects = [effects.bold_effect, effects.fade_in_effect]

    # Inside the loop where you create text objects
    for effect in selected_effects:
        effect.apply(text_obj)

