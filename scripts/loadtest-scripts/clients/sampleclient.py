import os

from .httpcodeexception import HTTPCodeException
import requests

sample_url = os.getenv('SAMPLE_URL', 'http://localhost:8125')


class SampleClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def upload_sample_file(self, filename):
        file_path = f'{script_directory()}/{filename}'
        survey_type = 'B'
        url = f'{sample_url}/samples/{survey_type}/fileupload'

        response = requests.post(url=url, auth=(self.username, self.password), files={'file': open(file_path, 'rb')})

        if response.status_code != requests.codes.created:
            raise HTTPCodeException(response.codes.created, response.status_code,
                                    f'Failed to upload sample file: {response.text}')

        return response.json()['id']


def script_directory():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
