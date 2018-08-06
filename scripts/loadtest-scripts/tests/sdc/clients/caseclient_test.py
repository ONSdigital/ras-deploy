import unittest
from unittest.mock import Mock

from requests import Response

from sdc.clients.caseclient import CaseClient


class CaseClientTest(unittest.TestCase):
    def setUp(self):
        self.http_client = Mock()
        self.client = CaseClient(self.http_client)

    def test_find_by_iac_makes_a_get_request_to_the_case_service(self):
        iac = '4d7bjg7s8gq6'

        self.client.find_by_iac(iac)

        self.http_client.get.assert_called_with(
            path='/cases/iac/4d7bjg7s8gq6',
            expected_status=200
        )

    def test_find_by_iac_returns_the_case_dict(self):
        content = b'{"x": 1}'
        response = Response()
        response._content = content
        response.encoding = 'utf-8'
        self.http_client.get.return_value = response

        case = self.client.find_by_iac('4d7bjg7s8gq6')

        self.assertEqual({'x': 1}, case)