from clients import http
from clients.actionclient import ActionClient
from clients.collectionexerciseclient import CollectionExerciseClient
from clients.http import factory


class SDCClient:
    def __init__(self, config):
        self.config = config

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
