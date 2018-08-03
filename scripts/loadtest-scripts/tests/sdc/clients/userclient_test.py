import unittest
from unittest.mock import Mock

from sdc.clients import userclient


class UserClientTest(unittest.TestCase):
    def setUp(self):
        self.http_client = Mock()
        self.client = userclient.UserClient(http_client=self.http_client)

    def test_enrol_fetches_the_case_by_iac(self):
        enrolment_code = '4d7bjg7s8gq6'

        self.client.register(
            email_address='user1@example.com',
            first_name='User',
            last_name='One',
            password='Top5ecret',
            telephone='0123456789',
            enrolment_code=enrolment_code
        )

        self.http_client.post.assert_called_with(
            path='/party-api/v1/respondents',
            json={
                'emailAddress': 'user1@example.com',
                'firstName': 'User',
                'lastName': 'One',
                'password': 'Top5ecret',
                'telephone': '0123456789',
                'enrolmentCode': enrolment_code,
                'status': 'CREATED',
            },
            expected_status=200
        )


def create_account(registration_data):
    logger.debug('Attempting to create account')

    url = f"{app.config['PARTY_URL']}/party-api/v1/respondents"
    registration_data['status'] = 'CREATED'
    response = requests.post(url, auth=app.config['PARTY_AUTH'], json=registration_data)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 400:
            message = 'Email has already been used'
        else:
            message = 'Failed to create account'
        raise ApiError(logger, response,
                       log_level='debug' if response.status_code == 400 else 'error',
                       message=message)

    logger.debug('Successfully created account')
