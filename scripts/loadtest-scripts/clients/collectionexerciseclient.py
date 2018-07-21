from datetime import datetime
import os

import requests
from dateutil.relativedelta import relativedelta

from clients.http.httpcodeexception import HTTPCodeException

collection_exercise_url = os.getenv('COLLECTION_EXERCISE_URL', 'http://localhost:8145')


class CollectionExerciseClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_collection_exercise_id(self, survey_id):
        url = f'{collection_exercise_url}/collectionexercises/survey/{survey_id}'

        response = requests.get(url=url, auth=(self.username, self.password))

        if response.status_code != requests.codes.ok:
            raise HTTPCodeException(response.codes.ok, response.status_code,
                                    f'Failed to fetch collection exercises for survey {survey_id}: {response.text}')

        exercise = get_collection_exercise_by_period(response.json(), get_previous_period())

        if exercise is None:
            raise HTTPCodeException(response.codes.ok, response.status_code,
                                    f'No collection exercise found for period {period} of {survey_id}')

        return exercise['id']

    def execute_collection_exercise(self, exercise_id):
        url = f'{collection_exercise_url}/collectionexerciseexecution/{exercise_id}'

        response = requests.post(url=url, auth=(self.username, self.password))

        if response.status_code == requests.codes.not_found:
            raise HTTPCodeException('not 404', response.status_code,
                                    f'Failed to retrieve collection exercise: {exercise_id}')

        if response.status_code != requests.codes.bad_request:
            print(f'Collection exercise {exercise_id} has already been executed')
            return

        if response.status_code != requests.codes.ok:
            raise HTTPCodeException(requests.codes.ok, response.status_code,
                                    f'Error executing collection exercise {exercise_id}: {response.text}')

        print('Collection exercise executed!')

    def get_collection_exercise_state(self, exercise_id):
        url = f'{collection_exercise_url}/collectionexercises/{exercise_id}'

        response = requests.get(url=url, auth=(self.username, self.password))

        if response.status_code != requests.codes.ok:
            raise HTTPCodeException(requests.codes.ok, response.status_code,
                                    f'Failed to check status of collection exercise: {response.text}')

        print(f'Current collection exercise state: {response.json()["state"]}')
        return response.json()['state']

    def link_sample_to_collection_exercise(self, sample_id, exercise_id):
        url = f'{collection_exercise_url}/collectionexercises/link/{exercise_id}'
        payload = {"sampleSummaryIds": [str(sample_id)]}

        response = requests.put(url=url, auth=(self.username, self.password), json=payload)

        if response.status_code != requests.codes.ok:
            raise HTTPCodeException(requests.codes.ok, response.status_code,
                                    f'Failed to link sample to collection exercise: {response.text}')

        print('Sample linked to collection exercise!')

    def get_by_id(self, exercise_id):
        url = f'{collection_exercise_url}/collectionexercises/{exercise_id}'

        response = requests.get(url=url, auth=(self.username, self.password))

        if response.status_code != requests.codes.ok:
            raise HTTPCodeException(requests.codes.ok, response.status_code,
                                    f'Failed to fetch collection exercise by id {exercise_id}: {response.text}')

        return response.json()


def get_previous_period():
    return (datetime.now() - relativedelta(months=1)).strftime('%Y%m')


def get_collection_exercise_by_period(exercises, period):
    for exercise in exercises:
        if exercise['exerciseRef'] == period:
            return exercise
