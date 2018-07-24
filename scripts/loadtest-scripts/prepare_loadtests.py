import os
import time
import logging

from clients import SDCClient, collectionexerciseclient
from clients.collectionexerciseclient import collection_exercise_url
from clients.collectioninstrumentclient import CollectionInstrumentClient
from clients.sampleclient import SampleClient

party_url = os.getenv('PARTY_URL', 'http://localhost:8081')
party_create_respondent_endpoint = os.getenv('PARTY_CREATE_RESPONDENT_ENDPOINT',
                                             '/party-api/v1/respondents')
action_url = os.getenv('ACTION_URL', 'http://localhost:8151')
iac_url = os.getenv('IAC_URL', 'http://localhost:8121')
survey_id = os.getenv('SURVEY_ID', '75b19ea0-69a4-4c58-8d7f-4458c8f43f5c')
survey_classifiers = os.getenv('SURVEY_CLASSIFIERS',
                               '{"form_type":"0102","eq_id":"1"}')
username = os.getenv('COLLECTION_INSTRUMENT_USERNAME', 'admin')
password = os.getenv('COLLECTION_INSTRUMENT_PASSWORD', 'secret')
polling_wait_time = int(os.getenv('POLLING_WAIT_TIME', '2'))
polling_retries = int(os.getenv('POLLING_RETRIES', '30'))
period_override = os.getenv('COLLECTION_EXERCISE_PERIOD', None)
logging_level = os.getenv('LOGGING_LEVEL', 'INFO')

ci = CollectionInstrumentClient(username, password)
sample = SampleClient(username, password)

config = {
    'service_username': username,
    'service_password': password,
    'action_url': action_url,
    'collection_exercise_url': collection_exercise_url,
}
sdc = SDCClient(config)


def with_timeout(action):
    count = 0
    while action():
        count += 1
        if count >= polling_retries:
            raise BaseException(f"Operation timed out")

        time.sleep(polling_wait_time)


def get_collection_exercise():
    exercise = sdc.collection_exercises.get_by_survey_and_period(
        survey_id,
        period_override or collectionexerciseclient.get_previous_period())

    logging.debug(f'Exercise ID = {exercise["id"]}')

    return exercise


def upload_and_link_collection_instrument(exercise_id):
    instrument_id = ci.get_collection_id_from_classifier(survey_classifiers)

    if instrument_id is None:
        ci.upload_collection_instrument(survey_id, survey_classifiers)
        instrument_id = ci.get_collection_id_from_classifier(survey_classifiers)
        logging.info(f'Created collection instrument, ID = {instrument_id}')
    else:
        logging.info(f'Collection instrument exists, ID = {instrument_id}')

    ci.link_collection_instrument_to_collection_exercise(instrument_id, exercise_id)


def upload_and_link_sample(csv, exercise_id):
    sample_id = sample.upload_sample_file(csv)
    logging.debug(f'Sample ID = {sample_id}')
    sdc.collection_exercises.link_sample_to_collection_exercise(sample_id, exercise_id)


def main():
    logging.basicConfig(level=logging.getLevelName(logging_level))
    exercise = get_collection_exercise()
    exercise_id = exercise['id']

    if sdc.collection_exercises.get_state(exercise_id) in ['LIVE', 'READY_FOR_LIVE']:
        logging.info('Quitting: The collection exercise has already been executed.')
        return

    # There is work in progress which will remove the need for this step
    sdc.actions.add_rule_for_collection_exercise(exercise_id)

    upload_and_link_collection_instrument(exercise_id)
    upload_and_link_sample('sample.csv', exercise_id)

    with_timeout(lambda: sdc.collection_exercises.get_state(exercise_id) not in ['READY_FOR_REVIEW'])

    sdc.collection_exercises.execute(exercise_id)

    with_timeout(lambda: sdc.collection_exercises.get_state(exercise_id) not in ['READY_FOR_LIVE', 'LIVE'])

main()
