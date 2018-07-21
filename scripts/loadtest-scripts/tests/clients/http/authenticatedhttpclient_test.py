import unittest
from unittest.mock import patch

from requests import Response

from clients.http.authenticatedhttpclient import AuthenticatedHTTPClient


class AuthenticatedHTTPClientTest(unittest.TestCase):
    USER = 'example-service-username'
    PASSWORD = 'very-secret-service-password'

    def setUp(self):
        self.client = AuthenticatedHTTPClient(self.USER, self.PASSWORD)

    @patch('requests.get')
    def test_get_delegates_request_to_requests_library(self, get):
        requests_response = Response()
        get.return_value = requests_response

        response = self.client.get(url='http://example.com',
                                   json={'ok': 'true'})

        get.assert_called_with(url='http://example.com',
                               json={'ok': 'true'},
                               auth=(self.USER, self.PASSWORD))
        self.assertEqual(requests_response, response)

    @patch('requests.post')
    def test_post_delegates_request_to_requests_library(self, post):
        requests_response = Response()
        post.return_value = requests_response

        response = self.client.post(url='http://example.com',
                                    json={'ok': 'true'})

        post.assert_called_with(url='http://example.com',
                                json={'ok': 'true'},
                                auth=(self.USER, self.PASSWORD))
        self.assertEqual(requests_response, response)
