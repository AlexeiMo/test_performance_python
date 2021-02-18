import json
from helpers.assertion_helper import assert_status_code
from helpers.json_helper import read_json

target = read_json('target.json')


class AuthorizationHelper:
    tokens = {"user": None, "admin": None}

    def authorize(self, session, email, password, role):
        if self.tokens[role]:
            return self.tokens[role]
        else:
            session.headers.update(
                {"Content-Type": "application/json"}
            )

            data = {
                "data": {
                    "email": f"{email}",
                    "password": f"{password}"
                }
            }
            with session.post(f"/{target['authorization']['host']}",
                              data=json.dumps(data),
                              name="/SIGN IN",
                              catch_response=True,
                              verify=False) as response:
                assert_status_code(response)
                rs_json = response.json()
            if not rs_json["data"]["refreshToken"]:
                response.failure("No authorization token found in response")
            else:
                token = rs_json["data"]["refreshToken"]
                self.tokens[role] = token
                cookie = response.cookies.get("token_signature")
                session.headers.update({
                    "Authorization": f"Bearer {token}",
                    "Cookie": f"token_signature={cookie}"
                })
            response.success()
            return None
