def assert_status_code(response, expected_status_code=200):
    if response.status_code != expected_status_code:
        response.failure(f"Status code is not correct ({response.status_code})")
    else:
        response.success()
