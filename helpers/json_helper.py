import json


def read_json(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    return data
