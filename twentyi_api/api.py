import requests
import json
import base64

class TwentyIRestAPI:
    def __init__(self, auth_url="https://auth-api.20i.com:3000",
                 url="https://api.20i.com", auth=None):
        self.url = url.rstrip('/')

        if isinstance(auth, dict):
            if "bearer" in auth and "username" in auth and "password" in auth:
                """Use reseller token, subuser username and subuser password to
                limit to subuser scope"""
                headers = {"Authorization": "Bearer {}".format(auth["bearer"])}
                o = {"grant_type": "password", "username": auth["username"],
                     "password": auth["password"]}
                r = requests.post(auth_url+"/login/authenticate", json=o,
                                  headers=headers)
                try:
                    token = self.token_to_bearer(r.json()["access_token"])
                    self.auth = token
                except ValueError as e:
                    raise Exception("Got unexpected response from login "
                                    "endpoint") from e
            elif "bearer" in auth and "username" in auth:
                """Use reseller token and subuser username to limit to subuser
                scope"""
                headers = {"Authorization": "Bearer {}".format(auth["bearer"])}
                r = []
                r.append(requests.get(auth_url+"/user/stack-user",
                                      headers=headers).json())
                r.append(requests.get(auth_url+"/user/service-user",
                                      headers=headers).json())
                username = None
                for user in r[0]:
                    if auth["username"] == user["name"]:
                        subuser_scope = "{}:{}".format(user["type"], user["id"])
                if subuser_scope is None:
                    raise Exception("Username not found in user list")
                o = {"grant_type": "client_credentials", "scope": subuser_scope}
                r = requests.post(auth_url+"/login/authenticate", json=o,
                                  headers=headers)
                try:
                    token = self.token_to_bearer(r.json()["access_token"])
                    self.auth = token
                except ValueError as e:
                    raise Exception("Got unexpected response from login "
                                    "endpoint") from e
            elif "bearer" in auth:
                """Use reseller token"""
                token = self.token_to_bearer(auth["bearer"])
                self.auth = token
            else:
                raise ValueError("Please supply authentication")
        else:
            raise ValueError("Please supply authentication")

    def token_to_bearer(self, token):
        token = token.encode()
        token = base64.b64encode(token)
        token = token.decode()
        return token

    def get_url(self, endpoint):
        return self.url + '/' + endpoint.lstrip('/')

    def decode_response(self, response):
        error = None
        try:
            jr = response.json()
            try:
                error = jr["error"]
                message = jr["message"]
            except:
                pass
        except json.decoder.JSONDecodeError as e:
            raise ValueError("No valid JSON was returned from the"
                             "server") from e
        if error is not None:
            print(json.dumps(error, indent=2))
        response.raise_for_status()
        return jr

    def get(self, endpoint=None, **kwargs):
        if endpoint is None:
            raise ValueError("no URL supplied")
        headers = {"Authorization": "Bearer {}".format(self.auth)}
        r = requests.get(self.get_url(endpoint), **kwargs, headers=headers)
        return self.decode_response(r)

    def post(self, endpoint=None, data=None, **kwargs):
        if endpoint is None:
            raise ValueError("no URL supplied")
        headers = {"Authorization": "Bearer {}".format(self.auth)}
        r = requests.post(self.get_url(endpoint), json=data, **kwargs,
                          headers=headers)
        return self.decode_response(r)
