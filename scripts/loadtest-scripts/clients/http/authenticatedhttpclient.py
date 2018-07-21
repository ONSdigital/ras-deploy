import requests


class AuthenticatedHTTPClient:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def get(self, **kwargs):
        auth = (self.username, self.password)

        return requests.get(**kwargs, auth=auth)

    def post(self, **kwargs):
        auth = (self.username, self.password)

        return requests.post(**kwargs, auth=auth)