import csv
import logging
from io import StringIO


class IACClient:
    def __init__(self, http_client, sftp_client, base_dir):
        self.http_client = http_client
        self.sftp_client = sftp_client
        self.base_dir = base_dir

    def download(self, period, generated_date, expected_codes):
        file = self._get_remote_filename(period, generated_date)
        csv_content = self.sftp_client.get(file).decode('utf-8')
        logging.debug(f'Downloaded file with content: {csv_content}')
        results = self._parse_file(csv_content, expected_codes)
        self.sftp_client.delete(file)

        return results

    def get_metadata_for(self, iac_code):
        response = self.http_client.get(path=f'/iacs/{iac_code}',
                                        expected_status=200)

        return response.json()

    def _get_remote_filename(self, period, generated_date):
        glob_pattern = f'BSNOT_*_{period}_{generated_date}_*.csv'
        glob_path = f'{self.base_dir}/{glob_pattern}'

        files = self.sftp_client.ls(self.base_dir, glob_pattern)

        self._assert_one_file_found(files, glob_path=glob_path)

        return f'{self.base_dir}/{files[0]}'

    @staticmethod
    def _assert_one_file_found(files, glob_path):
        if len(files) == 0:
            raise RemoteFileNotFoundException(glob_path=glob_path)

        if len(files) > 1:
            raise MultipleRemoteFilesFoundException(
                glob_path=glob_path,
                results=files)

    def _parse_file(self, csv_content, expected_codes):
        results = self._parse_colon_separated_string(csv_content)

        results = [r[1] for r in results]

        if len(results) != expected_codes:
            raise IncorrectNumberOfIACCodes(expected=expected_codes,
                                            results=results)
        return results

    @staticmethod
    def _parse_colon_separated_string(csv_content):
        csv_file_handle = StringIO(csv_content)

        return csv.reader(csv_file_handle, delimiter=':')


class RemoteFileNotFoundException(Exception):
    def __init__(self, glob_path):
        self.message = f"No files found matching '{glob_path}'"


class MultipleRemoteFilesFoundException(Exception):
    def __init__(self, glob_path, results):
        self.message = f"Expected 1 file matching '{glob_path}'; " + \
                       f"found {len(results)} - {results}"


class IncorrectNumberOfIACCodes(Exception):
    def __init__(self, expected, results):
        self.message = f"Expected {expected} IAC codes; " + \
                       f"got {len(results)} - {results}"

    def __str__(self):
        return self.message