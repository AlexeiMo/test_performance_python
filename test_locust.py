from pathlib import Path

from locust import HttpUser, between, task, TaskSet
import urllib3
import json

urllib3.disable_warnings()


class UserBehavior(TaskSet):

    def on_start(self):
        self.client.headers.update(
            {"Content-Type": "application/json"}
        )

        data = {
            "data": {
                "email": "",
                "password": ""
            }
        }
        with self.client.post("/users/public/v1/auth/signin",
                              data=json.dumps(data),
                              name="/SIGN IN",
                              catch_response=True,
                              verify=False) as response:
            if response.status_code != 200:
                response.failure(f"Status code is not correct ({response.status_code})")
            else:
                rs_json = response.json()
                if not rs_json["data"]["refreshToken"]:
                    response.failure("No authorization token found in response")
                else:
                    token = rs_json["data"]["refreshToken"]
                    self.client.headers.update(
                        {"Authorization": f"Bearer {token}"}
                    )
                    response.success()

    @task(1)
    def get_transaction(self):
        tr_id = 499262
        with self.client.get(f"/accounts/private/v1/user/transactions/{tr_id}",
                             name="/TRANSACTION",
                             catch_response=True,
                             verify=False) as response:
            if response.status_code != 200:
                response.failure(f"Status code is not correct ({response.status_code})")
            else:
                rs_json = response.json()
                if rs_json["data"]["id"] != tr_id:
                    response.failure(f"Incorrect transaction was given ({rs_json['data']['id']})")
                else:
                    response.success()

    @task(1)
    def get_user_profile(self):
        with self.client.get("/settings/private/v1/config/profile/user-options",
                             catch_response=True,
                             verify=False,
                             name="/PROFILE") as response:
            # import pdb; pdb.set_trace()
            if response.status_code != 200:
                response.failure(f"Status code is not correct ({response.status_code})")
            elif "User Information" not in response:
                response.failure("Invalid page was loaded")
            else:
                response.success()

    # @task(1)
    # def upload_file(self):
    #     filename = "9_10_5.csv"
    #     user_id = "42337c0a-4c44-4be7-8b2e-cf92ac4388cc"
    #     content_type = "text/csv"
    #     self.client.headers.update(
    #         {"Content-Type": f"{content_type}"}
    #     )
    #     file_to_open = Path("data") / filename
    #     with open(file_to_open, "rb") as file:
    #         files = {"file": (filename, file, content_type)}
    #         with self.client.post(f"/files/private/v1/files/private/{user_id}",
    #                               files=files,
    #                               catch_response=True,
    #                               name="/UPLOAD FILE",
    #                               verify=False) as response:
    #             # import pdb; pdb.set_trace()
    #             if response.status_code != 200:
    #                 response.failure(f"Status code is not correct ({response.status_code})")
    #             else:
    #                 rs_json = response.json()
    #                 file_id = rs_json["data"]["id"]
    #     with self.client.get(f"/files/private/v1/users/{user_id}",
    #                          catch_response=True,
    #                          name="/ALL FILES",
    #                          verify=False
    #                          ) as response:
    #         if response.status_code != 200:
    #             response.failure(f"Status code is not correct ({response.status_code})")
    #         else:
    #             rs_json = response.json()
    #             id_list = [item["id"] for item in rs_json["data"]["items"]]
    #             if file_id not in id_list:
    #                 response.failure("File not found")
    #             else:
    #                 response.success()


class LoadTestUser(HttpUser):
    wait_time = between(1, 2)
    host = "https://api-loadtest-01.ebanq-qa.com"
    tasks = [UserBehavior]
