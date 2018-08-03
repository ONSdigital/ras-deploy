import unittest
from unittest.mock import Mock, call

from requests import Response

from sdc.clients.iacclient import IACClient, RemoteFileNotFoundException, \
    MultipleRemoteFilesFoundException, IncorrectNumberOfIACCodes


class IACClientTest(unittest.TestCase):
    BASE_DIR = 'BSD'

    def setUp(self):
        self.sftp_client = Mock()
        self.sftp_client.ls = Mock()
        self.sftp_client.ls.return_value = ['a-file.csv']
        self.sftp_client.get = Mock()
        self.sftp_client.get.return_value = b''
        self.sftp_client.delete = Mock()

        self.http_client = Mock()

        self.iac_client = IACClient(http_client=self.http_client,
                                    sftp_client=self.sftp_client,
                                    base_dir=self.BASE_DIR)

    def test_download_checks_if_the_ls(self):
        self.iac_client.download(period='201806',
                                 generated_date='11062018',
                                 expected_codes=0)

        self.sftp_client.ls.assert_called_with(
            self.BASE_DIR, 'BSNOT_*_201806_11062018_*.csv')

    def test_download_raises_if_file_is_not_found(self):
        self.sftp_client.ls.return_value = []

        with self.assertRaises(RemoteFileNotFoundException) as context:
            self.iac_client.download(period='201804',
                                     generated_date='01042018',
                                     expected_codes=1)

        self.assertEqual(
            f"No files found matching "
            f"'{self.BASE_DIR}/BSNOT_*_201804_01042018_*.csv'",
            context.exception.message
        )

    def test_download_raises_if_multiple_files_are_found(self):
        self.sftp_client.ls.return_value = ['file1.csv', 'file2.csv']

        with self.assertRaises(MultipleRemoteFilesFoundException) as context:
            self.iac_client.download(period='201804',
                                     generated_date='01042018',
                                     expected_codes=2)
        self.assertEqual(
            f"Expected 1 file matching "
            f"'{self.BASE_DIR}/BSNOT_*_201804_01042018_*.csv'; "
            f"found 2 - ['file1.csv', 'file2.csv']",
            context.exception.message)

    def test_download_deletes_the_file_after_getting_it(self):
        self.sftp_client.ls.return_value = ['the-file.csv']

        self.iac_client.download(period='201807',
                                 generated_date='03072018',
                                 expected_codes=0)

        self.sftp_client.assert_has_calls(
            [call.get(f'{self.BASE_DIR}/the-file.csv'),
             call.delete(f'{self.BASE_DIR}/the-file.csv')])

    def test_download_returns_the_iac_codes(self):
        self.sftp_client.get.return_value = bytes(
            '49900000008:lpt3932m4yxs:NOTSTARTED:null:null:null:null:null:FE\n'
            '49900000007:p2js5r9m2gbz:NOTSTARTED:null:null:null:null:null:FE\n'
            '49900000005:5sypjcp7rjyg:NOTSTARTED:null:null:null:null:null:FE\n'
            '49900000006:22yr5vmdxbx6:NOTSTARTED:null:null:null:null:null:FE\n',
            'utf-8')

        result = self.iac_client.download(period='201807',
                                          generated_date='03072018',
                                          expected_codes=4)

        expected = [
            'lpt3932m4yxs',
            'p2js5r9m2gbz',
            '5sypjcp7rjyg',
            '22yr5vmdxbx6'
        ]

        self.assertEqual(expected, result)

    def test_download_does_not_delete_if_the_content_is_bad(self):
        self.sftp_client.get.return_value = \
            'bad\n' + \
            'con:tent\n'

        with self.assertRaises(Exception):
            self.iac_client.download(period='201807',
                                     generated_date='03072018',
                                     expected_codes=2)

        self.sftp_client.delete.assert_not_called()

    def test_download_does_not_delete_the_file_if_not_expected_num_of_iacs(
            self):
        self.sftp_client.get.return_value = bytes(
            '49900000008:lpt3932m4yxs:NOTSTARTED:null:null:null:null:null:FE\n'
            '49900000007:p2js5r9m2gbz:NOTSTARTED:null:null:null:null:null:FE\n'
            '49900000005:5sypjcp7rjyg:NOTSTARTED:null:null:null:null:null:FE\n'
            '49900000006:22yr5vmdxbx6:NOTSTARTED:null:null:null:null:null:FE\n',
            'utf-8')

        with self.assertRaises(IncorrectNumberOfIACCodes) as context:
            self.iac_client.download(period='201807',
                                     generated_date='03072018',
                                     expected_codes=5)

        self.assertEqual(
            "Expected 5 IAC codes; got 4 - ["
            "'lpt3932m4yxs', 'p2js5r9m2gbz', '5sypjcp7rjyg', '22yr5vmdxbx6'"
            "]",
            context.exception.message)

    def test_get_metadata_for_makes_a_get_request_to_the_iac_service(self):
        self._mock_http_get_reponse(b'{}')

        iac_code = 'lpt3932m4yxs'

        self.iac_client.get_metadata_for(iac_code)

        self.http_client.get.assert_called_with(
            path=f'/iacs/{iac_code}',
            expected_status=200)

    def test_get_metadata_for_returns_the_dict(self):
        self._mock_http_get_reponse(b'{"x": "1"}')

        metadata = self.iac_client.get_metadata_for('lpt3932m4yxs')

        self.assertEqual({'x': '1'}, metadata)

    def _mock_http_get_reponse(self, content):
        response = Response()
        response._content = content
        response.encoding = 'utf-8'
        self.http_client.get = Mock()
        self.http_client.get.return_value = response
