import json
from os import path

import pynotif

PATH_TO_CONFIG = path.abspath(path.join(path.dirname(pynotif.__file__), '..', 'configuration.json'))


def load_config():
    with open(PATH_TO_CONFIG, 'r') as config:
        return json.load(config)
