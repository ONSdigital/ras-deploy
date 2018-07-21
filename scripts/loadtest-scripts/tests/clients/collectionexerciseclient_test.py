import unittest
from unittest.mock import Mock, MagicMock, patch

from requests import Response

from clients.collectionexerciseclient import CollectionExerciseClient
from clients.http.httpcodeexception import HTTPCodeException


class CollectionExerciseClientTest(unittest.TestCase):
    EXERCISE_ID = '66d6ac26-9bca-4f60-a87a-1bd1f792710c'
    SERVICE_USERNAME = 'example-user'
    SERVICE_PASSWORD = 'example-pass'

    def setUp(self):
        self.http_response = Response()
        self.http_response.status_code = 200

        self.http_client = Mock()
        self.http_client.post = MagicMock(return_value=self.http_response)

        self.client = CollectionExerciseClient(self.SERVICE_USERNAME,
                                               self.SERVICE_PASSWORD)

    @patch('requests.get')
    def test_get_collection_exercise_makes_a_get_request(self, get):
        http_response = self._http_response(b'{"example": "value"}', 200)
        get.return_value = http_response

        self.client.get_collection_exercise(self.EXERCISE_ID)

        get.assert_called_with(
            url=f'http://localhost:8145/collectionexercises/{self.EXERCISE_ID}',
            auth=(self.SERVICE_USERNAME, self.SERVICE_PASSWORD))

    @patch('requests.get')
    def test_get_collection_exercise_returns_the_exercise(self, get):
        http_response = self._http_response(b'{"example": "value"}', 200)
        get.return_value = http_response

        result = self.client.get_collection_exercise(self.EXERCISE_ID)

        self.assertEqual({'example': 'value'}, result)

    @patch('requests.get')
    def test_get_collection_exercise_raises_if_request_failed(self, get):
        http_response = self._http_response(b'Error', 500)
        get.return_value = http_response

        with (self.assertRaises(HTTPCodeException)):
            self.client.get_collection_exercise(self.EXERCISE_ID)

    def _http_response(self, content, status_code):
        http_response = Response()
        http_response.status_code = status_code
        http_response._content = content
        http_response.encoding = 'utf-8'
        return http_response
