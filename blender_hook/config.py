import os
import json


CONFIG_FORMATTING = dict(
    Addon=os.path.basename(os.getcwd()),
)


try:
    with open('blender.json', 'r') as json_file:
        config = json.load(json_file)
        dict_stack = [config]
        while dict_stack:
            d = dict_stack.pop()
            for key, value in d.items():
                if isinstance(value, dict):
                    dict_stack.append(value)
                elif isinstance(value, str):
                    d[key] = value.format(**CONFIG_FORMATTING)
except:
    config = None
