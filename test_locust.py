import os
from pathlib import Path

from locust import HttpUser, between, task, TaskSet
import urllib3

from helpers import csv_helper
from helpers import requests_helper
from helpers.auth_helper import AuthorizationHelper
from helpers.assertion_helper import assert_status_code
from helpers.json_helper import read_json

urllib3.disable_warnings()

filepath = os.path.abspath("target.json")
target = read_json(filepath)

auth_helper = AuthorizationHelper()


class UserBehavior(TaskSet):
    # @task(1)
    class UserModule(TaskSet):

        def on_start(self):
            token = auth_helper.authorize(
                session=self.client,
                email=target["authorization"]["user"]["email"],
                password=target["authorization"]["user"]["password"],
                role="user"
            )
            if token:
                self.client.headers.update({
                    "Authorization": f"Bearer {token}"
                })
            self.client.headers.update(
                {"Content-Type": "application/json"}
            )

        # @task(1)
        def create_tba_request(self):
            filename = target["user_tba_request"]["filename"]
            tan_filename = target["user_tba_request"]["tan_filename"]
            endpoint = target["user_tba_request"]["endpoint"]

            csv_helper.change_tan(self.client, filename, tan_filename)

            requests_helper.send_post_request(self.client, endpoint, "/USER TBA REQUEST", filename)

        # @task(5)
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

        # @task(5)
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

        @task(3)
        def stop(self):
            self.interrupt()

    @task(1)
    class AdminModule(TaskSet):

        def on_start(self):
            token = auth_helper.authorize(
                session=self.client,
                email=target["authorization"]["admin"]["email"],
                password=target["authorization"]["admin"]["password"],
                role="admin"
            )
            if token:
                self.client.headers.update({
                    "Authorization": f"Bearer {token}"
                })
            self.client.headers.update(
                {"Content-Type": "application/json"}
            )

        # @task(1)
        def create_tba_request(self):
            filename = target["tba_request"]["filename"]
            endpoint = target["tba_request"]["endpoint"]
            request_type = target["tba_request"]["subject"]
            user_id = target["authorization"]["user"]["user_id"]
            response = requests_helper.create_request(self.client, filename, user_id, endpoint)
            request_id = response["data"]["id"]
            requests_helper.verify_request_details(self.client, request_id, request_type)

        # @task(1)
        def create_tbu_request(self):
            filename = target["tbu_request"]["filename"]
            endpoint = target["tbu_request"]["endpoint"]
            request_type = target["tbu_request"]["subject"]
            user_id = target["authorization"]["user"]["user_id"]
            response = requests_helper.create_request(self.client, filename, user_id, endpoint)
            request_id = response["data"]["id"]
            requests_helper.verify_request_details(self.client, request_id, request_type)

        # @task(1)
        def create_owt_request(self):
            filename = target["owt_request"]["filename"]
            endpoint = target["owt_request"]["endpoint"]
            request_type = target["owt_request"]["subject"]
            user_id = target["authorization"]["user"]["user_id"]
            response = requests_helper.create_request(self.client, filename, user_id, endpoint)
            request_id = response["data"]["id"]
            requests_helper.verify_request_details(self.client, request_id, request_type)

        # @task(1)
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
            requests_helper.verify_request_details(self.client, request_id, request_type)

        @task(1)
        def navigate_to_incoming_messages(self):
            filename = target["incoming_messages"]["filename"]
            endpoint = target["incoming_messages"]["endpoint"]

            requests_helper.send_get_request(self.client, endpoint, "/INCOMING MESSAGES", filename)

        # @task(1)
        def navigate_to_newsletters(self):
            filename = target["newsletters"]["filename"]
            endpoint = target["newsletters"]["endpoint"]

            requests_helper.send_get_request(self.client, endpoint, "/NEWSLETTERS", filename)

        # @task(1)
        def import_user_profiles(self):
            filename1 = target["user_profiles_import"]["filename1"]
            filename2 = target["user_profiles_import"]["filename2"]
            endpoint = target["user_profiles_import"]["endpoint"]

            csv_helper.create_new_import_users_file(filename1)

            requests_helper.import_csv_file(self.client, endpoint, "/USER PROFILES IMPORT 100", filename2)

        # @task(1)
        def import_transactions(self):
            filename = target["transactions_import"]["filename"]
            endpoint = target["transactions_import"]["endpoint"]

            requests_helper.import_csv_file(self.client, endpoint, "/TRANSACTIONS IMPORT 100", filename)

        # @task(1)
        def import_transfer_requests(self):
            filename = target["get_pending_requests"]["filename"]
            endpoint = target["get_pending_requests"]["endpoint"]

            request_id = requests_helper.send_get_request(self.client, endpoint, "/TRANSFER REQUESTS", filename)["data"][0]["id"]
            status = "Executed"

            filename1 = target["transfer_requests_import"]["filename1"]
            filename2 = target["transfer_requests_import"]["filename2"]
            endpoint = target["transfer_requests_import"]["endpoint"]

            csv_helper.create_new_import_requests_file(filename1, request_id, status)

            requests_helper.import_csv_file(self.client, endpoint, "/TRANSFER REQUESTS IMPORT 500", filename2)

        @task(1)
        def stop(self):
            self.interrupt()


class LoadTestUser(HttpUser):
    wait_time = between(0.3, 0.5)
    host = "https://api-loadtest-01.ebanq-qa.com"

    tasks = [UserBehavior]
