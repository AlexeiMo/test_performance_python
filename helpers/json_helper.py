import json


def read_json(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    return data


def write_json(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)
