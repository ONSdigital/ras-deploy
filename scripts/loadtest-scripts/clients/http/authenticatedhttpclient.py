import requests


class AuthenticatedHTTPClient:
    def __init__(self, client, username: str, password: str):
        self.client = client
        self.username = username
        self.password = password

    def get(self, **kwargs):
        auth = (self.username, self.password)

        return self.client.get(**kwargs, auth=auth)

    def post(self, **kwargs):
        auth = (self.username, self.password)

        return self.client.post(**kwargs, auth=auth)