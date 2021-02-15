from pathlib import Path

from locust import HttpUser, between, task, TaskSet
import urllib3
from helpers.requests_helper import create_request, get_request_by_id, verify_request_details
from helpers.auth_helper import AuthorizationHelper
from helpers.assertion_helper import assert_status_code
from helpers.json_helper import read_json

urllib3.disable_warnings()

target = read_json('target.json')


class UserBehavior(TaskSet):
    @task(1)
    class UserModule(TaskSet):

        def on_start(self):
            AuthorizationHelper().authorize(
                session=self.client,
                email=target["authorization"]["user"]["email"],
                password=target["authorization"]["user"]["password"],
                role="user"
            )

        @task(1)
        def get_transaction(self):
            tr_id = target["transactions"]["id"]
            with self.client.get(f"/{target['transactions']['host']}/{tr_id}",
                                 name="/TRANSACTION",
                                 catch_response=True,
                                 verify=False) as response:
                assert_status_code(response)
                rs_json = response.json()
                if rs_json["data"]["id"] != tr_id:
                    response.failure(f"Incorrect transaction was given ({rs_json['data']['id']})")
                else:
                    response.success()

        @task(1)
        def get_user_profile(self):
            with self.client.get(f"/{target['user-profile']['host']}",
                                 catch_response=True,
                                 verify=False,
                                 name="/PROFILE") as response:
                assert_status_code(response)
                if response.text == "":
                    response.failure("Page not loaded")
                else:
                    response.success()

        @task(1)
        def upload_file(self):
            self.client.headers.update({
                "Content-Type": None
            })
            filename = target["files"]["filename"]
            user_id = target["authorization"]["user"]["user_id"]
            content_type = target["files"]["content_type"]
            file_to_open = Path("data") / filename
            with open(file_to_open, "rb") as file:
                files = {"file": (filename, file, content_type)}
                with self.client.post(f"/{target['files']['host']}/files/private/{user_id}",
                                      files=files,
                                      catch_response=True,
                                      name="/UPLOAD FILE",
                                      verify=False) as response:
                    assert_status_code(response)
                    rs_json = response.json()
                    file_id = rs_json["data"]["id"]
            with self.client.get(f"/{target['files']['host']}/users/{user_id}",
                                 catch_response=True,
                                 name="/ALL FILES",
                                 verify=False
                                 ) as response:
                assert_status_code(response)
                rs_json = response.json()
                id_list = [item["id"] for item in rs_json["data"]["items"]]
                if file_id not in id_list:
                    response.failure("File not found")
                else:
                    response.success()

        @task(1)
        def stop(self):
            self.interrupt()

    @task(1)
    class AdminModule(TaskSet):

        def on_start(self):
            AuthorizationHelper().authorize(
                session=self.client,
                email=target["authorization"]["admin"]["email"],
                password=target["authorization"]["admin"]["password"],
                role="admin"
            )
            self.client.headers.update(
                {"Content-Type": "application/json"}
            )

        @task(1)
        def create_tba_request(self):
            filename = target["tba_request"]["filename"]
            endpoint = target["tba_request"]["endpoint"]
            request_type = target["tba_request"]["subject"]
            user_id = target["authorization"]["user"]["user_id"]
            response = create_request(self.client, filename, user_id, endpoint)
            request_id = response["data"]["id"]
            response = get_request_by_id(self.client, request_id)
            verify_request_details(response, request_id, request_type)

        @task(1)
        def create_tbu_request(self):
            filename = target["tbu_request"]["filename"]
            endpoint = target["tbu_request"]["endpoint"]
            request_type = target["tbu_request"]["subject"]
            user_id = target["authorization"]["user"]["user_id"]
            response = create_request(self.client, filename, user_id, endpoint)
            request_id = response["data"]["id"]
            response = get_request_by_id(self.client, request_id)
            verify_request_details(response, request_id, request_type)

        @task(1)
        def create_owt_request(self):
            filename = target["owt_request"]["filename"]
            endpoint = target["owt_request"]["endpoint"]
            request_type = target["owt_request"]["subject"]
            user_id = target["authorization"]["user"]["user_id"]
            response = create_request(self.client, filename, user_id, endpoint)
            request_id = response["data"]["id"]
            response = get_request_by_id(self.client, request_id)
            verify_request_details(response, request_id, request_type)

        @task(1)
        def create_ca_request(self):
            filename = target["ca_request"]["filename"]
            endpoint = target["ca_request"]["endpoint"]
            request_type = target["ca_request"]["subject"]
            source_file = Path("data") / filename
            with open(source_file, "rb") as data:
                with self.client.post(f"/{target['requests']['host']}/admin/{endpoint}", data=data,
                                      name=f"/{endpoint}", catch_response=True, verify=False) as response:
                    assert_status_code(response)
                    rs_json = response.json()
                request_id = rs_json["data"]["id"]
            response = get_request_by_id(self.client, request_id)
            verify_request_details(response, request_id, request_type)

        @task(1)
        def stop(self):
            self.interrupt()


class LoadTestUser(HttpUser):
    wait_time = between(1, 2)
    host = "https://api-loadtest-01.ebanq-qa.com"

    tasks = [UserBehavior]
