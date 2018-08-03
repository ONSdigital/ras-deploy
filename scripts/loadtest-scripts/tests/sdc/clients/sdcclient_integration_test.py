import json
import unittest
from datetime import datetime, timedelta
from io import StringIO

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
            'case_url': 'http://case.services.com',
            'iac_url': 'http://iac.services.com',
            'collection_exercise_url': 'http://localhost:8145',
            'collection_instrument_url': 'http://ci.services.com',
            'sample_url': 'http://sample.services.com',
            'sftp_host': 'sftp.example.com',
            'sftp_port': 22,
            'actionexporter_sftp_password': 'sftp-password',
            'actionexporter_sftp_username': 'sftp-username',
            'party_url': 'http://party.services.com',
            'party_create_respondent_endpoint': '/party-api/v1/respondents',
        }

        config.update(override)

        return config

    @httpretty.activate
    def test_actions(self):
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

        yesterday = datetime.now() - timedelta(days=1)

        self.client.actions.add_rule_for_collection_exercise(
            exercise_id=exercise_id,
            trigger_time=yesterday)

    @httpretty.activate
    def test_collection_exercises(self):
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

    @httpretty.activate
    def test_samples(self):
        sample_id = '1429b8df-d657-44bb-a59a-7a298d4ed08f'

        httpretty.register_uri(
            httpretty.POST,
            'http://sample.services.com/samples/B/fileupload',
            body=json.dumps({'id': sample_id}),
            status=201)

        file = StringIO('file contents')
        result = self.client.samples.upload_file(file)

        self.assertEqual(sample_id, result)

    @httpretty.activate
    def test_collection_instruments(self):
        survey_id = '6ee65e4d-ecc0-4144-936c-d87c0775b383'
        survey_classifiers = {'classifier': 'xxx'}

        httpretty.register_uri(
            httpretty.POST,
            'http://ci.services.com/collection-instrument-api/1.0.2/upload',
            body='',
            status=200)

        self.client.collection_instruments.upload(
            survey_id=survey_id,
            survey_classifiers=survey_classifiers)

    @httpretty.activate
    def test_cases_property(self):
        iac_code = 'p2js5r9m2gbz'

        httpretty.register_uri(
            httpretty.GET,
            f'http://case.services.com/cases/iac/{iac_code}',
            body=json.dumps({'id': 'case-id'}),
            status=200)

        case = self.client.cases.find_by_iac(iac_code)
        self.assertEqual({'id': 'case-id'}, case )

    @httpretty.activate
    def test_users(self):
        iac_code = 'p2js5r9m2gbz'

        httpretty.register_uri(
            httpretty.POST,
            f'http://party.services.com/party-api/v1/respondents',
            body=json.dumps({}),
            status=200)

        self.client.users.register(
            email_address='user1@example.com',
            first_name='User',
            last_name='One',
            password='Top5ecret',
            telephone='0123456789',
            enrolment_code=iac_code)
