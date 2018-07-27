import json
import unittest

import httpretty
import pytest

from sdc.clients import SDCClient


@pytest.mark.usefixtures('sftpserver')
class SDCClientIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.client = SDCClient(self._config())

    def _config(self, override={}):
        config = {
            'service_username': 'example-service-username',
            'service_password': 'example-service-password',
            'action_url': 'http://action.services.com',
            'collection_exercise_url': 'http://localhost:8145',
            'sftp_host': 'sftp.example.com',
            'sftp_port': 22,
            'actionexporter_sftp_password': 'sftp-password',
            'actionexporter_sftp_username': 'sftp-username',
            'iac_url': 'http://iac.services.com',
            'party_url': 'http://party.services.com',
            'party_create_respondent_endpoint': '/party-api/v1/respondents',
        }

        config.update(override)

        return config

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
            body=json.dumps('OK'),
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

    def test_iac_codes(self):
        files = {
            'BSD': {
                'BSNOT_11_201806_11062018_999.csv':
                    '49900000008:iac-code:NOTSTARTED:null:null:null:null:null:FE\n'}}

        with self.sftpserver.serve_content(files):
            client = SDCClient(self._config({
                'sftp_host': self.sftpserver.host,
                'sftp_port': self.sftpserver.port,
                'actionexporter_sftp_username': 'the-username',
                'actionexporter_sftp_password': 'the-password',
            }))

            codes = client.iac_codes.download(period='201806',
                                              generated_date='11062018',
                                              expected_codes=1)

            self.assertEquals(['iac-code'], codes)
