import os
import json


CONFIG_FORMATTING = dict(
    Addon=os.path.basename(os.getcwd()),
)


try:
    with open('blender_config.json', 'r') as json_file:
        config = json.load(json_file)
        for key, value in config.items():
            config[key] = value.format(**CONFIG_FORMATTING)
except:
    config = None
