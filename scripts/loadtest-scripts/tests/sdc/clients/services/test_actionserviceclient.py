import unittest
from datetime import timedelta, datetime
from unittest.mock import Mock

from sdc.clients.services import ActionServiceClient


class TestActionServiceClient(unittest.TestCase):
    def setUp(self):
        self.http_client = Mock()
        self.client = ActionServiceClient(self.http_client)

    def test_create_action_rule_makes_a_post(self):
        business_case_action_plan_id = 'ce47573d-8a57-41ca-b289-49a2416c5731'

        yesterday = datetime.now() - timedelta(days=1)

        self.client.create_action_rule(
            action_plan_id=business_case_action_plan_id,
            action_type_name='BSNL',
            name='BSNL Name',
            description='BSNL Description',
            trigger_date_time=yesterday,
            priority=1
        )

        iso_yesterday = yesterday.strftime("%Y-%m-%dT%H:%M:00.000+0000")

        self.http_client.post.assert_called_with(
            path='/actionrules',
            expected_status=201,
            json={'actionPlanId': business_case_action_plan_id,
                  'actionTypeName': 'BSNL',
                  'name': 'BSNL Name',
                  'description': 'BSNL Description',
                  'triggerDateTime': iso_yesterday,
                  'priority': 1})
