import logging
import os
from datetime import datetime

from dateutil.relativedelta import relativedelta

collection_exercise_url = os.getenv('COLLECTION_EXERCISE_URL',
                                    'http://localhost:8145')


class CollectionExerciseClient:
    def __init__(self, http_client):
        self.http_client = http_client

    def get_by_survey_and_period(self, survey_id, period):
        path = f'/collectionexercises/survey/{survey_id}'

        response = self.http_client.get(path=path)

        exercise = self._get_collection_exercise_by_period(response.json(), period)

        if exercise is None:
            raise Exception(
                f'No collection exercise found for period {period} of {survey_id}')

        return exercise

    def execute(self, exercise_id):
        path = f'/collectionexerciseexecution/{exercise_id}'

        self.http_client.post(path=path, expected_status=200)

        logging.info('Collection exercise executed!')

    def get_state(self, exercise_id):
        state = self.get_by_id(exercise_id)['state']

        logging.debug(f'Current collection exercise state: {state}')

        return state

    def link_sample_to_collection_exercise(self, sample_id, exercise_id):
        path = f'/collectionexercises/link/{exercise_id}'
        payload = {"sampleSummaryIds": [str(sample_id)]}

        self.http_client.put(path=path, json=payload)

        logging.info('Sample linked to collection exercise!')

    def get_by_id(self, exercise_id):
        response = self.http_client.get(path=f'/collectionexercises/{exercise_id}')

        return response.json()

    @staticmethod
    def _get_collection_exercise_by_period(exercises, period):
        for exercise in exercises:
            if exercise['exerciseRef'] == period:
                return exercise


def get_previous_period():
    return (datetime.now() - relativedelta(months=1)).strftime('%Y%m')
