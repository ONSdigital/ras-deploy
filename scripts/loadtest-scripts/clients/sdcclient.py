from clients import http
from clients.actionclient import ActionClient
from clients.collectionexerciseclient import CollectionExerciseClient
from clients.http import factory
from clients.iac_client import IACClient
from clients.sftpclient import SFTPClient


class SDCClient:
    def __init__(self, config):
        self.config = config
        self.sftp_client = None

    @property
    def actions(self):
        http_client = http.factory.create(
            base_url=self.config['action_url'],
            username=self.config['service_username'],
            password=self.config['service_password'])

        return ActionClient(http_client=http_client,
                            collection_exercise_client=self.collection_exercises)

    @property
    def collection_exercises(self):
        http_client = http.factory.create(
            base_url=self.config['collection_exercise_url'],
            username=self.config['service_username'],
            password=self.config['service_password'])

        return CollectionExerciseClient(http_client)

    @property
    def iac_codes(self):
        if not self.sftp_client:
            self.sftp_client = SFTPClient(
                host=self.config['sftp_host'],
                username=self.config['actionexporter_sftp_username'],
                password=self.config['actionexporter_sftp_password'],
                port=self.config['sftp_port'])

        return IACClient(sftp_client=self.sftp_client, base_dir='BSD')
