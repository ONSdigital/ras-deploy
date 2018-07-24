import csv
from io import StringIO


class IACClient:
    def __init__(self, sftp_client, base_dir):
        self.sftp_client = sftp_client
        self.base_dir = base_dir

    def download(self, period, generated_date, expected_codes):
        file = self._get_remote_filename(period, generated_date)
        csv_content = self.sftp_client.get(file)
        results = self._parse_file(csv_content, expected_codes)

        self.sftp_client.delete(file)

        return results

    def _get_remote_filename(self, period, generated_date):
        glob_pattern = f'{self.base_dir}/BSNOT_*_{period}_{generated_date}_*.csv'

        files = self.sftp_client.ls(glob_pattern)

        self._assert_one_file_found(files, glob_pattern=glob_pattern)

        return files[0]

    @staticmethod
    def _assert_one_file_found(files, glob_pattern):
        if len(files) == 0:
            raise RemoteFileNotFoundException(glob_pattern=glob_pattern)

        if len(files) > 1:
            raise MultipleRemoteFilesFoundException(
                glob_pattern=glob_pattern,
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
    def __init__(self, glob_pattern):
        self.message = f"No files found matching '{glob_pattern}'"


class MultipleRemoteFilesFoundException(Exception):
    def __init__(self, glob_pattern, results):
        self.message = f"Expected 1 file matching '{glob_pattern}'; " + \
                       f"found {len(results)} - {results}"


class IncorrectNumberOfIACCodes(Exception):
    def __init__(self, expected, results):
        self.message = f"Expected {expected} IAC codes; " + \
                       f"got {len(results)} - {results}"
