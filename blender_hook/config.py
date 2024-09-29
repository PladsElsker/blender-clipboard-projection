import os
import json


CONFIG_FORMATTING = dict(
    Addon=os.path.basename(os.getcwd())
)


with open('blender_hook/config.json', 'r') as json_file:
    config = json.load(json_file)
    for key, value in config.items():
        config[key] = value.format(**CONFIG_FORMATTING)
