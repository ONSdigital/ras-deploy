import time
import requests
import os

from clients.collectionexerciseclient import CollectionExerciseClient
from clients.collectioninstrumentclient import CollectionInstrumentClient
from clients.sampleclient import SampleClient

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

ce = CollectionExerciseClient(username, password)
ci = CollectionInstrumentClient(username, password)
sample = SampleClient(username, password)


# Enrolment

def create_enrolment_codes(count):
    url = f'{iac_url}/iacs'
    payload = {'count': count, 'createdBy': 'loadtest'}

    response = requests.post(url=url, auth=(username, password), json=payload)

    if response.status_code != requests.codes.created:
        error_exit(f'Failed to create IACs: {response.text}')

    print(f'Set up {count} IACs')
    return response.json()


def error_exit(message):
    print(message)
    exit(1)


def with_timeout(action):
    count = 0
    while action():
        count += 1
        if count >= polling_retries:
            error_exit('Timed out')

        time.sleep(polling_wait_time)


def create_user(email_address, first_name, last_name, user_password, telephone,
                enrolment_code):
    url = f'{party_url}{party_create_respondent_endpoint}'
    payload = {'emailAddress': email_address,
               'firstName': first_name,
               'lastName': last_name,
               'password': user_password,
               'telephone': telephone,
               'enrolmentCode': enrolment_code,
               }

    response = requests.post(url=url, auth=(username, password), json=payload)

    print(response.status_code)
    if response.status_code != requests.codes.created:
        error_exit(
            f'Failed to create user with email {email_address}: {response.text}')

    return 'magic link thing'


# Main support

def get_collection_exercise():
    exercise_id = ce.get_collection_exercise_id(survey_id)
    print(f'Exercise ID = {exercise_id}')

    return exercise_id


def upload_and_link_collection_instrument(exercise_id):
    instrument_id = ci.get_collection_id_from_classifier(survey_classifiers)

    if instrument_id is None:
        ci.upload_collection_instrument(survey_id, survey_classifiers)
        instrument_id = ci.get_collection_id_from_classifier(survey_classifiers)
        print(f'Created collection instrument, ID = {instrument_id}')
    else:
        print(f'Collection instrument exists, ID = {instrument_id}')

    ci.link_collection_instrument_to_collection_exercise(instrument_id, exercise_id)


def upload_and_link_sample(csv, exercise_id):
    sample_id = sample.upload_sample_file(csv)
    print(f'Sample ID = {sample_id}')
    ce.link_sample_to_collection_exercise(sample_id, exercise_id)


def main():
    exercise_id = get_collection_exercise()

    if ce.get_collection_exercise_state(exercise_id) in ['LIVE', 'READY_FOR_LIVE']:
        print('Quitting: The collection exercise has already been executed.')
        return

    upload_and_link_collection_instrument(exercise_id)
    upload_and_link_sample('sample.csv', exercise_id)

    with_timeout(lambda: ce.get_collection_exercise_state(exercise_id) not in ['READY_FOR_REVIEW'])

    ce.execute_collection_exercise(exercise_id)

    with_timeout(lambda: ce.get_collection_exercise_state(exercise_id) not in ['READY_FOR_LIVE', 'LIVE'])

    # get_iac_codes_for_all_cases_for_collect(exercise_id)
    #
    # enrolment_codes = create_enrolment_codes(1)
    # for enrolment_code in enrolment_codes:
    #     verify_link = create_user(enrolment_code=enrolment_code,
    #                               email_address='something@somewhere.com',
    #                               user_password='secret',
    #                               first_name='unique',
    #                               last_name='name',
    #                               telephone='01234567890')
    #     # verify_user(verify_link)
    #
    # exit(0)


main()
