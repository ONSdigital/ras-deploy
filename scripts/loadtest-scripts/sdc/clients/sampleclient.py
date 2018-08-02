import os

from sdc.clients.http.httpcodeexception import HTTPCodeException
import requests

sample_url = os.getenv('SAMPLE_URL', 'http://localhost:8125')


class SampleClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def upload_sample_file(self, filename):
        survey_type = 'B'
        url = f'{sample_url}/samples/{survey_type}/fileupload'

        response = requests.post(
            url=url,
            auth=(self.username, self.password),
            files={'file': open(filename, 'rb')})

        if response.status_code != requests.codes.created:
            raise HTTPCodeException(
                requests.codes.created,
                response.status_code,
                f'Failed to upload sample file: {response.text}')

        return response.json()['id']
