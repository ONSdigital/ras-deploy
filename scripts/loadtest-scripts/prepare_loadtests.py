import datetime
import logging
import os
import time

from sdc.clients import SDCClient, collectionexerciseclient
from sdc.clients.collectionexerciseclient import collection_exercise_url
from sdc.clients.collectioninstrumentclient import CollectionInstrumentClient
from sdc.clients.iac_client import RemoteFileNotFoundException
from sdc.clients.sampleclient import SampleClient

party_url = os.getenv('PARTY_URL', 'http://localhost:8081')
party_create_respondent_endpoint = os.getenv('PARTY_CREATE_RESPONDENT_ENDPOINT',
                                             '/party-api/v1/respondents')
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
    'action_url': os.getenv('ACTION_URL', 'http://localhost:8151'),
    'collection_exercise_url': collection_exercise_url,
    'sftp_host': os.getenv('SFTP_HOST'),
    'sftp_port': int(os.getenv('SFTP_PORT', '22')),
    'actionexporter_sftp_username':
        os.getenv('ACTION_EXPORTER_SFTP_USERNAME'),
    'actionexporter_sftp_password':
        os.getenv('ACTION_EXPORTER_SFTP_PASSWORD'),
}
sdc = SDCClient(config)


def wait_for(action):
    count = 0
    result = action()
    while not result:
        count += 1
        if count >= polling_retries:
            raise BaseException(f"Operation timed out")

        time.sleep(polling_wait_time)
        result = action()

    return result


def get_collection_exercise():
    exercise = sdc.collection_exercises.get_by_survey_and_period(
        survey_id,
        collection_exercise_period())

    logging.debug(f'Exercise ID = {exercise["id"]}')

    return exercise


def collection_exercise_period():
    return period_override or collectionexerciseclient.get_previous_period()


def upload_and_link_collection_instrument(exercise_id):
    instrument_id = ci.get_collection_id_from_classifier(survey_classifiers)

    if instrument_id is None:
        ci.upload_collection_instrument(survey_id, survey_classifiers)
        instrument_id = ci.get_collection_id_from_classifier(survey_classifiers)
        logging.info(f'Created collection instrument, ID = {instrument_id}')
    else:
        logging.info(f'Collection instrument exists, ID = {instrument_id}')

    ci.link_collection_instrument_to_collection_exercise(instrument_id,
                                                         exercise_id)


def upload_and_link_sample(csv, exercise_id):
    sample_id = sample.upload_sample_file(csv)

    logging.debug(f'Sample ID = {sample_id}')

    sdc.collection_exercises \
        .link_sample_to_collection_exercise(sample_id, exercise_id)


def download_iac_codes(period, expected_codes):
    try:
        today = datetime.date.today().strftime('%d%m%Y')

        return sdc.iac_codes.download(
            period=collection_exercise_period(),
            generated_date=today,
            expected_codes=expected_codes)
    except (RemoteFileNotFoundException):
        return None


def main():
    logging.basicConfig(level=logging.getLevelName(logging_level))
    exercise = get_collection_exercise()
    exercise_id = exercise['id']

    if sdc.collection_exercises.get_state(exercise_id) in ['LIVE',
                                                           'READY_FOR_LIVE']:
        logging.info(
            'Quitting: The collection exercise has already been executed.')
        return

    # There is work in progress which will remove the need for this step
    sdc.actions.add_rule_for_collection_exercise(exercise_id)

    upload_and_link_collection_instrument(exercise_id)
    upload_and_link_sample('sample.csv', exercise_id)

    # Magic number: should be taken from num lines in sample file
    sample_size = 1

    wait_for(lambda: sdc.collection_exercises.get_state(exercise_id) in [
        'READY_FOR_REVIEW'])

    sdc.collection_exercises.execute(exercise_id)

    wait_for(lambda: sdc.collection_exercises.get_state(exercise_id) in [
        'READY_FOR_LIVE', 'LIVE'])

    iac_codes = wait_for(lambda: download_iac_codes(
        period=collection_exercise_period(),
        expected_codes=sample_size))

    print(iac_codes)


main()
