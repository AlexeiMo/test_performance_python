import os
from pathlib import Path
from helpers.assertion_helper import assert_status_code
from helpers.json_helper import read_json

filepath = os.path.abspath("target.json")
target = read_json(filepath)


def get_request_by_id(session, request_id):
    with session.get(f"/{target['requests']['host']}/requests/{request_id}",
                     catch_response=True, verify=False, name="/REQUESTS/[ID]") as response:
        assert_status_code(response)
        rs_json = response.json()
    return rs_json


def create_request(session, filename, user_id, endpoint):
    source_file = Path("data") / filename
    with open(source_file, "rb") as data:
        with session.post(f"/{target['requests']['host']}/admin/{endpoint}/user/{user_id}", data=data,
                          name=f"/{endpoint}", catch_response=True, verify=False) as response:
            assert_status_code(response)
            rs_json = response.json()
        return rs_json


def verify_request_details(session, request_id, request_type):
    with session.get(f"/{target['requests']['host']}/requests/{request_id}",
                     catch_response=True, verify=False, name="/REQUESTS/[ID]") as response:
        assert_status_code(response)
        rs_json = response.json()
        response_type = rs_json['data']['request']['request']['subject']
        response_id = rs_json['data']['request']['request']['id']
        if request_id != response_id:
            response.failure(f"Invalid response id ({response_id} instead of {request_id})")
        elif request_type != response_type:
            response.failure(f"Invalid response type ({response_type} instead of {request_type})")
        else:
            response.success()


def send_get_request(session, url, request_name, filename=None):
    if filename:
        source_file = Path("data") / filename
        params = read_json(source_file)
    else:
        params = None
    with session.get(url, name=request_name, params=params, verify=False,
                     catch_response=True) as response:
        assert_status_code(response)
