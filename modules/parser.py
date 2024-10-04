# modules/parser.py

import json

def parse_data(json_path):
    """
    Parses the JSON file and returns a list of chunks.
    Each chunk is a dictionary with 'text' and 'timestamp' keys.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        chunks = data.get('chunks', [])
        if not chunks:
            print("No chunks found in data.")
            return None

        return chunks

    except FileNotFoundError:
        print(f"File not found: {json_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None
def parse_visual_elements(json_path):
    """
    Parses the visual elements JSON file and returns a list of visual elements.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        visual_elements = data.get('visual_elements', [])
        if not visual_elements:
            print("No visual elements found.")
            return []

        # Validate and process visual elements
        for element in visual_elements:
            # Validate required keys
            required_keys = ['file_path', 'type', 'timestamp', 'media']
            for key in required_keys:
                if key not in element:
                    raise ValueError(f"Visual element missing required key: {key}")

            # Validate 'type'
            if element['type'] not in ['background', 'overlay',"main"]:
                raise ValueError(f"Invalid type '{element['type']}' in visual element.")

            # Validate 'media'
            if element['media'] not in ['image', 'video']:
                raise ValueError(f"Invalid media '{element['media']}' in visual element.")

            # Validate 'timestamp'
            if not isinstance(element['timestamp'], list) or len(element['timestamp']) != 2:
                raise ValueError("Timestamp must be a list of two elements [start_time, end_time].")

            # Ensure 'effects' is a list
            if 'effects' not in element or not isinstance(element['effects'], list):
                element['effects'] = []

        return visual_elements

    except FileNotFoundError:
        print(f"Visual elements file not found: {json_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON decode error in visual elements file: {e}")
        return []
    except ValueError as e:
        print(f"Data validation error: {e}")
        return []