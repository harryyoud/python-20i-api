import requests
import json
import base64

from requests import HTTPError


class TwentyIRestAPI:
    def __init__(self, auth_url="https://auth-api.20i.com:3000",
                 url="https://api.20i.com", auth=None):
        """Process and store token used for authenticating to the REST API

        Keyword arguments:
         - str(auth_url) = the URL used for subuser authentication. defaults to
                      https://auth-api.20i.com:3000 if not given
         - str(url) = the URL used for the REST API commands. defaults to
                      https://api.20i.com if not given
         - dict(auth) = only bearer being set results in reseller level access
                        both bearer and username being set results in scope
                        limited to subuser access
                        bearer, username and password being set results in
                        scope being limited to subuser access
                        {
                          "bearer": reseller_token
                          "username": (optional) subuser_username
                          "password": (optional) subuser_password
                        }
        """

        # We add this ourselves, remove it now to prevent double slash
        self.url = url.rstrip('/')

        if isinstance(auth, dict):
            if "bearer" in auth and "username" in auth and "password" in auth:
                """Use reseller token, subuser username and subuser password to
                limit to subuser scope"""
                o = {"grant_type": "password", "username": auth["username"],
                     "password": auth["password"]}
                r = requests.post(auth_url+"/login/authenticate", json=o,
                                  headers=self._build_headers(auth["bearer"]))
                try:
                    token = self._token_to_bearer(r.json()["access_token"])
                    self.auth = token
                except ValueError as e:
                    raise Exception("Got unexpected response from login "
                                    "endpoint") from e
            elif "bearer" in auth and "username" in auth:
                """Use reseller token and subuser username to limit to subuser
                scope"""
                headers = self._build_headers(auth["bearer"])
                r = requests.get(auth_url+"/user/stack-user",
                                      headers=headers).json()
                r.append(requests.get(auth_url+"/user/service-user",
                                      headers=headers).json())
                username = None
                for user in r:
                    try:
                        if auth["username"] == user["name"]:
                            subuser_scope = "{}:{}".format(user["type"], user["id"])
                    except KeyError:
                        pass
                if subuser_scope is None:
                    raise Exception("Username not found in user list")
                o = {"grant_type": "client_credentials", "scope": subuser_scope}
                r = requests.post(auth_url+"/login/authenticate", json=o,
                                  headers=headers)
                try:
                    token = self._token_to_bearer(r.json()["access_token"])
                    self.auth = token
                except ValueError as e:
                    raise Exception("Got unexpected response from login "
                                    "endpoint") from e
            elif "bearer" in auth:
                """Use reseller token"""
                token = self._token_to_bearer(auth["bearer"])
                self.auth = token
            else:
                raise ValueError("Please supply authentication")
        else:
            raise ValueError("Please supply authentication")

    def _token_to_bearer(self, token):
        """base64 encode given token for use in HTTP headers

        Keyword arguments:
         - str(token) - Usually looks something like c6d7b42a36fcd2625
        """
        token = token.encode()
        token = base64.b64encode(token)
        token = token.decode()
        return token

    def _get_url(self, endpoint):
        """Return URL from combining api URL and endpoint, stripping slashes

        Keyword arguments:
         - str(endpoint) - looks something like "/package/example.com/domain"
        """
        return self.url + '/' + endpoint.lstrip('/')

    def _decode_response(self, response):
        """Extract JSON from response or return an error if unable

        Keyword arguments:
         - response - requests module response type
        """
        jr = {}
        try:
            jr = response.json()
            response.raise_for_status()
        except json.decoder.JSONDecodeError as e:
            raise APIError(message="No valid JSON was returned from the"
                                   "server") from e
        except HTTPError as e:
            raise APIError(error=jr['error'] if 'error' in jr else None) from e
        return jr

    def _build_headers(self, auth=None):
        if auth is None:
            auth = self.auth
        return {
                   "Authorization": "Bearer {}".format(auth)
               }

    def get(self, endpoint=None, **kwargs):
        """GET the endpoint and return the response as JSON if decodable

        Keyword arguments:
         - str(endpoint) - Looks something like "/package/example.com/domain"
         - **kwargs - all other keyword args are passed to requests.get
        """
        if endpoint is None:
            raise ValueError("no URL supplied")
        r = requests.get(self._get_url(endpoint), **kwargs,
                         headers=self._build_headers())
        return self._decode_response(r)

    def post(self, endpoint=None, data=None, **kwargs):
        """POST the endpoint with given data (if supplied) and return the
        response as a dict if JSON-decodable

        Keyword arguments:
         - str(endpoint) - Looks something like "/domain/example.com/dns"
         - dict(data) - JSON body sent to server
         - **kwargs - all other keyword args are passed to requests.post
        """
        if endpoint is None:
            raise ValueError("no URL supplied")
        headers = {"Authorization": "Bearer {}".format(self.auth)}
        r = requests.post(self._get_url(endpoint), json=data, **kwargs,
                          headers=self._build_headers())
        return self._decode_response(r)


class APIError(Exception):
    def __init__(self, message="TwentyI REST API Error", error=None):
        super().__init__(message)
        self.message = message
        self.error = error

    def __str__(self):
        if self.error:
            if 'message' in self.error:
                return f"{self.message}: {self.error['message']}"
            return f"{self.message}: {self.error}"
        else:
            return self.message
