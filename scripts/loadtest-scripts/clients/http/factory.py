import requests

from clients.http.authenticatedhttpclient import AuthenticatedHTTPClient
from clients.http.baseurlhttpclient import BaseURLHTTPClient
from clients.http.statuscodecheckinghttpclient import \
    StatusCodeCheckingHTTPClient


def create(base_url, username, password):
    return BaseURLHTTPClient(
        StatusCodeCheckingHTTPClient(
            AuthenticatedHTTPClient(requests, username, password)),
        base_url)
