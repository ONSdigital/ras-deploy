import unittest
from unittest.mock import Mock, MagicMock

from requests import Response

from clients.actionclient import ActionClient


class ActionClientTest(unittest.TestCase):
    EXERCISE_ID = '9281d5b4-c1bf-4322-9f34-683b266bc3b2'
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
        self.collection_exercise_client.get_by_id = MagicMock(
            return_value=self.COLLECTION_EXERCISE)

        self.client = ActionClient(http_client=self.http_client,
                                   collection_exercise_client=self.collection_exercise_client)

    def test_add_action_rule_fetches_the_collection_exercise(self):
        self.client.add_rule_for_collection_exercise(self.EXERCISE_ID)

        self.collection_exercise_client.get_by_id \
            .assert_called_with(self.EXERCISE_ID)

    def test_add_action_rule_makes_a_post_request(self):
        self.client.add_rule_for_collection_exercise(self.EXERCISE_ID)

        self.http_client.post.assert_called_with(
            path='/actionrules',
            expected_status=201,
            json={'actionPlanId': self.BUSINESS_CASE_ACTION_PLAN_ID,
                  'actionTypeName': 'BSNL',
                  'name': 'BSNL+0',
                  'description': 'Description for BSNL+0',
                  'daysOffset': 0,
                  'priority': 1}
        )
