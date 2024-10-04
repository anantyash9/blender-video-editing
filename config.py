# config.py
import math
CONFIG = {
    # General Settings
    'FRAME_RATE': 24,
    'RESOLUTION': (1080, 1920),  # Width x Height for portrait mode
    'OUTPUT_PATH': 'D:\\workspace\\blender\\output\\video.mp4',
    'BACKGROUND_COLOR': (0, 0, 0, 1),  # Black background

    # Effects to Apply
    'EFFECTS': [
        'bold_effect',
        'fade_in_effect',
        'typewriter_effect'
    ],

    # Asset Paths
    'FONT_PATH': 'D:\\workspace\\blender\\assets\\fonts\\',
    'DEFAULT_FONT': 'BebasNeue-Regular.ttf',
    'BOLD_FONT': 'Roboto-Bold.ttf',

    # Other Settings
    'TEXT_COLOR': (1, 1, 1, 1),  # White text
    'TEXT_SIZE': 1.0,
    'SCENE_NAME': 'Scene',
    # ... (other configurations)
    'CAMERA_DISTANCE': 10,  # Distance from the text to the camera
    'CAMERA_FOCAL_LENGTH': 50,  # Focal length of the camera
    # ... (other configurations)
    'MAX_SCALE': 1.0,                   # Maximum scaling factor
    'CAMERA_ADJUST_STEP': 0.5,          # Step size for camera adjustments
    'MIN_FOV': math.radians(10),        # Minimum field of view in radians
    'SCALE_PADDING': 0.75,
    'CAMERA_ORTHO_SCALE': 5,
}
