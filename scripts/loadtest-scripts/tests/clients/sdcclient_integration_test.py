import json
import unittest

import httpretty

from clients import SDCClient


class SDCClientIntegrationTest(unittest.TestCase):
    def setUp(self):
        config = {
            'service_username': 'example-service-username',
            'service_password': 'example-service-password',
            'action_url': 'http://action.services.com',
            'collection_exercise_url': 'http://localhost:8145',
        }
        self.client = SDCClient(config)

    @httpretty.activate
    def test_action_client(self):
        exercise_id = '1429b8df-d657-44bb-a59a-7a298d4ed08f'

        collection_exercise = {
            'caseTypes': [
                {
                    'actionPlanId': 'BUSINESS_CASE_ACTION_PLAN_ID',
                    'sampleUnitType': 'B'
                }
            ]
        }
        httpretty.register_uri(
            httpretty.GET,
            f'http://localhost:8145/collectionexercises/{exercise_id}',
            body=json.dumps(collection_exercise),
            status=200)

        httpretty.register_uri(
            httpretty.POST,
            f'http://action.services.com/actionrules',
            body=json.dumps(collection_exercise),
            status=201)

        self.client.actions.add_rule_for_collection_exercise(exercise_id)

    @httpretty.activate
    def test_collection_exercise_client(self):
        exercise_id = '1429b8df-d657-44bb-a59a-7a298d4ed08f'

        collection_exercise = {
            'caseTypes': [
                {
                    'actionPlanId': 'BUSINESS_CASE_ACTION_PLAN_ID',
                    'sampleUnitType': 'B'
                }
            ]
        }
        httpretty.register_uri(
            httpretty.GET,
            f'http://localhost:8145/collectionexercises/{exercise_id}',
            body=json.dumps(collection_exercise),
            status=200)

        result = self.client.collection_exercises.get_by_id(exercise_id)

        self.assertEqual(collection_exercise, result)


