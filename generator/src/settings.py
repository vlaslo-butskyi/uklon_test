import json
import os

current_path = os.path.abspath(os.path.dirname(__file__))
with open(f'{current_path}/settings.json') as f:
    config = json.load(f)
