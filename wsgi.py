import json
from os import path

import pynotif
from pynotif.src.notifier import Notifier

PATH_TO_CONFIG = path.abspath(path.join(path.dirname(pynotif.__file__), '..', 'development.json'))


def load_config():
    with open(PATH_TO_CONFIG, 'r') as config:
        return json.load(config)


def load_app():
    conf = load_config()
    n = Notifier(config=conf)
    n.serve()

load_app()
