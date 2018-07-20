import unittest
from unittest.mock import Mock, MagicMock

from requests import Response

from clients.actionclient import ActionClient
from clients.httpcodeexception import HTTPCodeException


class ActionClientTest(unittest.TestCase):
    ACTION_SERVICE_URL = 'https://rm-action-service.cloudfoundry'
    EXERCISE_ID = '9281d5b4-c1bf-4322-9f34-683b266bc3b2'
    SERVICE_USERNAME = 'example.username'
    SERVICE_PASSWORD = 't0p5ecret'
    BUSINESS_CASE_ACTION_PLAN_ID = '4d8be6f8-492e-4ef9-b741-d178499736dd'
    COLLECTION_EXERCISE = {
        'caseTypes': [
            {
                'actionPlanId': BUSINESS_CASE_ACTION_PLAN_ID,
                'sampleUnitType': 'B'
            },
            {
                'actionPlanId': '739a2d07-6804-41eb-b6d2-5d8332f04abe',
                'sampleUnitType': 'BI'
            }
        ]}

    def setUp(self):
        self.http_response = Response
        self.http_response.status_code = 201

        self.http_client = Mock()
        self.http_client.post = MagicMock(return_value=self.http_response)

        self.collection_exercise_client = Mock()
        self.collection_exercise_client.get_collection_exercise = MagicMock(
            return_value=self.COLLECTION_EXERCISE)

        self.client = ActionClient(http_client=self.http_client,
                                   collection_exercise_client=self.collection_exercise_client,
                                   service_url=self.ACTION_SERVICE_URL,
                                   service_username=self.SERVICE_USERNAME,
                                   service_password=self.SERVICE_PASSWORD)

    def test_add_action_rule_fetches_the_collection_exercise(self):
        self.client.add_action_rule_to_collection_exercise(self.EXERCISE_ID)

        self.collection_exercise_client \
            .get_collection_exercise \
            .assert_called_with(self.EXERCISE_ID)

    def test_add_action_rule_makes_a_post_request(self):
        self.client.add_action_rule_to_collection_exercise(self.EXERCISE_ID)

        self.http_client.post.assert_called_with(
            url=f'{self.ACTION_SERVICE_URL}/actionrules',
            auth=(self.SERVICE_USERNAME, self.SERVICE_PASSWORD),
            json={'actionPlanId': self.BUSINESS_CASE_ACTION_PLAN_ID,
                  'actionTypeName': 'BSNL',
                  'name': 'BSNL+0',
                  'description': 'Description for BSNL+0',
                  'daysOffset': 0,
                  'priority': 1}
        )

    def test_add_action_rule_raises_if_status_code_is_not_201(self):
        self.http_response.status_code = 400

        self.collection_exercise_client.get_collection_exercise = Mock(
            return_value={
                'caseTypes': [
                    {
                        'actionPlanId': '739a2d07-6804-41eb-b6d2-5d8332f04abe',
                        'sampleUnitType': 'B'
                    }
                ]})

        with (self.assertRaises(HTTPCodeException)):
            self.client.add_action_rule_to_collection_exercise(self.EXERCISE_ID)
