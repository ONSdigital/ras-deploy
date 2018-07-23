import json
import unittest
from unittest.mock import Mock, MagicMock

from requests import Response

from clients.collectionexerciseclient import CollectionExerciseClient
from clients.http.httpcodeexception import HTTPCodeException


class CollectionExerciseClientTest(unittest.TestCase):
    def setUp(self):
        self.http_response = Response()
        self.http_response.status_code = 200

        self.http_client = Mock()
        self.http_client.post = MagicMock(return_value=self.http_response)

        self.client = CollectionExerciseClient(http_client=self.http_client)

    def test_get_by_id(self):
        http_response = self._http_response(b'{"example": "value"}', 200)
        self.http_client.get.return_value = Mock()
        self.http_client.get.return_value = http_response

        exercise_id = '66d6ac26-9bca-4f60-a87a-1bd1f792710c'

        result = self.client.get_by_id(exercise_id)

        self.http_client.get.assert_called_with(
            path=f'/collectionexercises/{exercise_id}')
        self.assertEqual({'example': 'value'}, result)

    def test_get_state(self):
        http_response = self._http_response(b'{"state": "LIVE"}', 200)
        self.http_client.get.return_value = Mock()
        self.http_client.get.return_value = http_response

        exercise_id = '66d6ac26-9bca-4f60-a87a-1bd1f792710c'

        result = self.client.get_state(exercise_id)

        self.http_client.get.assert_called_with(
            path=f'/collectionexercises/{exercise_id}')
        self.assertEqual('LIVE', result)

    def test_link_sample_to_collection_exercise(self):
        http_response = self._http_response(b'{"state": "LIVE"}', 200)
        self.http_client.put.return_value = Mock()
        self.http_client.put.return_value = http_response

        exercise_id = '66d6ac26-9bca-4f60-a87a-1bd1f792710c'
        sample_id = '33989db1-2cc0-4459-a939-7292003d0340'

        self.client.link_sample_to_collection_exercise(sample_id, exercise_id)

        self.http_client.put.assert_called_with(
            path=f'/collectionexercises/link/{exercise_id}',
            json={'sampleSummaryIds': [sample_id]})

    def test_execute_makes_posts_to_the_collection_exercise_service(self):
        exercise_id = '66d6ac26-9bca-4f60-a87a-1bd1f792710c'

        self.client.execute(exercise_id)

        self.http_client.post.assert_called_with(
            path=f'/collectionexerciseexecution/{exercise_id}',
            expected_status=200)

    def test_get_by_survey_and_period(self):
        exercises = [
            {'exerciseRef': '201805'},
            {'exerciseRef': '201806'},
        ]

        http_response = self._http_response(bytes(json.dumps(exercises), 'utf-8'), 200)
        self.http_client.get.return_value = Mock()
        self.http_client.get.return_value = http_response

        survey_id = '66d6ac26-9bca-4f60-a87a-1bd1f792710c'

        exercise = self.client.get_by_survey_and_period(survey_id, '201805')

        self.http_client.get.assert_called_with(
            path=f'/collectionexercises/survey/{survey_id}')
        self.assertEqual({'exerciseRef': '201805'}, exercise)

    def test_get_by_survey_and_period_raises_if_exercise_not_found(self):
        http_response = self._http_response(b'[]', 200)
        self.http_client.get.return_value = Mock()
        self.http_client.get.return_value = http_response

        survey_id = '66d6ac26-9bca-4f60-a87a-1bd1f792710c'

        with self.assertRaises(Exception):
            self.client.get_by_survey_and_period(survey_id, '201802')

    @staticmethod
    def _http_response(content, status_code):
        http_response = Response()
        http_response.status_code = status_code
        http_response._content = content
        http_response.encoding = 'utf-8'

        return http_response
