import time
import requests
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

collection_instrument_url = \
    os.getenv('COLLECTION_INSTRUMENT_URL',
              'http://localhost:8002')
collection_instrument_search_endpoint = \
    os.getenv('COLLECTION_INSTRUMENT_SEARCH_ENDPOINT',
              '/collection-instrument-api/1.0.2/collectioninstrument')
collection_instrument_upload_endpoint = \
    os.getenv('COLLECTION_INSTRUMENT_UPLOAD_ENDPOINT',
              '/collection-instrument-api/1.0.2/upload')
collection_instrument_link_endpoint = \
    os.getenv('COLLECTION_INSTRUMENT_LINK_ENDPOINT',
              '/collection-instrument-api/1.0.2/link-exercise')
sample_url = \
    os.getenv('SAMPLE_URL',
              'http://localhost:8125')
collection_exercise_url = \
    os.getenv('COLLECTION_EXERCISE_URL', 'http://localhost:8145')
survey_id = os.getenv('SURVEY_ID', '75b19ea0-69a4-4c58-8d7f-4458c8f43f5c')
survey_classifiers = os.getenv('SURVEY_CLASSIFIERS', '{"form_type":"0102","eq_id":"1"}')
username = os.getenv('COLLECTION_INSTRUMENT_USERNAME', 'admin')
password = os.getenv('COLLECTION_INSTRUMENT_PASSWORD', 'secret')
polling_wait_time = int(os.getenv('POLLING_WAIT_TIME', '2'))

# Collection instrument

def upload_collection_instrument():
    upload_params = {'survey_id': survey_id, 'classifiers': survey_classifiers}
    url = collection_instrument_url + collection_instrument_upload_endpoint

    response = requests.post(url=url, params=upload_params, auth=(username, password))

    if response.status_code != requests.codes.ok:
        error_exit(f'Failed to set collection instrument: {response.text}')

def link_collection_instrument_to_collection_exercise(instrument_id, exercise_id):
    url = f'{collection_instrument_url}{collection_instrument_link_endpoint}/{instrument_id}/{exercise_id}'

    response = requests.post(url=url, auth=(username,password))

    if response.status_code != requests.codes.ok:
        error_exit(f'Failed to link collection instrument to exercise: {response.text}')

    print('Collection instrument linked to exercise!')


def get_collection_id_from_classifier(classifiers):
    search_params = {'searchString': classifiers}
    url = collection_instrument_url + collection_instrument_search_endpoint

    response = requests.get(url=url, params=search_params, auth=(username, password))

    if response.status_code != requests.codes.ok:
        error_exit(f'Failed to check for collection instrument: {response.text}')

    results = response.json()
    return results[0]['id'] if len(results) > 0 else None

# Collection exercise

def get_previous_period():
    return (datetime.now() - relativedelta(months=1)).strftime('%Y%m')

def get_collection_exercise_by_period(exercises, period):
    for exercise in exercises:
        if exercise['exerciseRef'] == period:
            return exercise

def get_collection_exercise_id(survey_id, period):
    url = f'{collection_exercise_url}/collectionexercises/survey/{survey_id}'

    response = requests.get(url=url, auth=(username, password))

    if response.status_code != requests.codes.ok:
        error_exit(f'Failed fetch collection exercises for survey {survey_id}: {response.text}')

    exercise = get_collection_exercise_by_period(response.json(), period)

    if exercise is None:
        error_exit(f'No collection exercise found for period {period} of {survey_id}')

    return exercise['id']


def execute_collection_exercise(exercise_id):
    url = f'{collection_exercise_url}/collectionexerciseexecution/{exercise_id}'

    response = requests.post(url=url, auth=(username, password))

    if response.status_code == requests.codes.not_found:
        error_exit(f'Failed to retrieve collection exercise: {exercise_id}')

    if response.status_code != requests.codes.bad_request:
        print(f'Collection exercise {exercise_id} has already been executed')
        return

    if response.status_code != requests.codes.ok:
        error_exit(f'Error executing collection exercise {exercise_id}: {response.text}')

    print('Collection exercise executed!')

def get_collection_exercise_state(exercise_id):
    url = f'{collection_exercise_url}/collectionexercises/{exercise_id}'

    response = requests.get(url=url, auth=(username, password))

    if response.status_code != requests.codes.ok:
        error_exit(f'Failed to check status of collection exercise: {response.text}')

    print(f'Current collection exercise state: {response.json()["state"])}')
    return response.json()['state']


def link_sample_to_collection_exercise(sample_id, exercise_id):
    url = f'{collection_exercise_url}/collectionexercises/link/{exercise_id}'
    payload = {"sampleSummaryIds": [str(sample_id)]}

    response = requests.put(url=url, auth=(username, password), json=payload)

    if response.status_code != requests.codes.ok:
        error_exit(f'Failed to link sample to collection exercise: {response.text}')

    print('Sample linked to collection exercise!')

# Sample

def upload_sample_file(filename):
    file_path = f'{script_directory()}/{filename}'
    survey_type = 'B'
    url = f'{sample_url}/samples/{survey_type}/fileupload'

    response = requests.post(url=url, auth=(username, password), files={'file': open(file_path, 'rb')})

    if response.status_code != requests.codes.created:
        error_exit(f'Failed to upload sample file: {response.text}')

    return response.json()['id']


def script_directory():
    return os.path.dirname(os.path.realpath(__file__))


def error_exit(message):
    print(message)
    exit(1)


def main():
    instrument_id = get_collection_id_from_classifier(survey_classifiers)

    if instrument_id is None:
        upload_collection_instrument()
        instrument_id = get_collection_id_from_classifier(survey_classifiers)
        print(f'Created collection instrument, ID = {instrument_id}')
    else:
        print(f'Collection instrument exists, ID = {instrument_id}')

    sample_id = upload_sample_file('sample.csv')
    print(f'Sample ID = {sample_id}')

    period = get_previous_period()
    print(f'Fetching collection exercise for {period}')

    exercise_id = get_collection_exercise_id(survey_id, period)
    print(f'Exercise ID = {exercise_id}')

    link_sample_to_collection_exercise(sample_id, exercise_id)
    
    link_collection_instrument_to_collection_exercise(instrument_id, exercise_id)

    while(get_collection_exercise_state(exercise_id) != 'READY_FOR_LIVE'):
        time.sleep(polling_wait_time)

    execute_collection_exercise(exercise_id)
    exit(0)

main()
