import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

from sdc.clients.actions import Actions


class ActionsTest(unittest.TestCase):
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
        self.collection_exercise_client = Mock()
        self.collection_exercise_client.get_by_id.return_value = \
            self.COLLECTION_EXERCISE

        self.action_service_client = Mock()

        self.client = Actions(collection_exercise_client=self.collection_exercise_client,
                              action_service_client=self.action_service_client)

    def test_add_action_rule_fetches_the_collection_exercise(self):
        self.client.add_rule_for_collection_exercise(
            exercise_id=self.EXERCISE_ID,
            trigger_time=datetime.now())

        self.collection_exercise_client.get_by_id \
            .assert_called_with(self.EXERCISE_ID)

    def test_add_action_rule_makes_a_request_to_the_action_service(self):
        yesterday = datetime.now() - timedelta(days=1)

        self.client.add_rule_for_collection_exercise(
            exercise_id=self.EXERCISE_ID,
            trigger_time=yesterday)

        self.action_service_client.create_action_rule.assert_called_with(
            action_plan_id=self.BUSINESS_CASE_ACTION_PLAN_ID,
            action_type_name='BSNL',
            name=f'BSNL-{yesterday}',
            description=f'Description for BSNL-{yesterday}',
            trigger_date_time=yesterday,
            priority=1)
