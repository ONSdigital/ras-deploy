import datetime
import json
import logging
import os

from sdc import csvfile
from sdc.clients import SDCClient, collectionexerciseclient, sdcclient
from sdc.clients.collectioninstrumentclient import CollectionInstrumentClient
from sdc.utils import wait_for, logger

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

SURVEY_ID = os.getenv('SURVEY_ID', '75b19ea0-69a4-4c58-8d7f-4458c8f43f5c')
SURVEY_CLASSIFIERS = os.getenv('SURVEY_CLASSIFIERS',
                               '{"form_type":"0102","eq_id":"1"}')

PERIOD_OVERRIDE = os.getenv('COLLECTION_EXERCISE_PERIOD', None)

logger.initialise_from_env()

config = sdcclient.config_from_env()
ci = CollectionInstrumentClient(config['service_username'],
                                config['service_password'])
sdc = SDCClient(config)


def collection_exercise_period():
    return PERIOD_OVERRIDE or collectionexerciseclient.get_previous_period()


def upload_and_link_collection_instrument(survey_id,
                                          survey_classifiers,
                                          collection_instruments,
                                          exercise_id):
    instrument_id = ci.get_collection_id_from_classifier(survey_classifiers)

    if instrument_id is None:
        ci.upload_collection_instrument(survey_id, survey_classifiers)
        instrument_id = ci.get_collection_id_from_classifier(survey_classifiers)
        logging.info(f'Created collection instrument, ID = {instrument_id}')
    else:
        logging.info(f'Collection instrument exists, ID = {instrument_id}')

    collection_instruments.link_collection_instrument_to_collection_exercise(
        instrument_id,
        exercise_id)


def upload_and_link_sample(sdc, csv, exercise_id):
    with open(csv, 'rb') as fh:
        sample_id = sdc.samples.upload_file(fh)

    logging.debug(f'Sample ID = {sample_id}')

    sdc.collection_exercises \
        .link_sample_to_collection_exercise(sample_id, exercise_id)

    return sample_id


def main():
    survey_id = SURVEY_ID
    exercise_period = collection_exercise_period()
    sample_file = f'{SCRIPT_DIR}/sample.csv'
    sample_size = csvfile.num_lines(filename=sample_file, delimiter=':')

    exercise = sdc.collection_exercises.get_by_survey_and_period(
        survey_id,
        exercise_period)

    logging.debug(f'Exercise ID = {exercise["id"]}')

    exercise_id = exercise['id']

    if sdc.collection_exercises.get_state(exercise_id) in ['LIVE',
                                                           'READY_FOR_LIVE']:
        logging.info(
            'Quitting: The collection exercise has already been executed.')
        return

    # There is work in progress which will remove the need for this step
    sdc.actions.add_rule_for_collection_exercise(exercise_id)

    upload_and_link_collection_instrument(
        survey_id=survey_id,
        survey_classifiers=SURVEY_CLASSIFIERS,
        collection_instruments=ci,
        exercise_id=exercise_id)

    sample_id = upload_and_link_sample(sdc=sdc, csv=sample_file, exercise_id=exercise_id)
    logging.debug(f'Uploaded sample with {sample_size} sample units.')

    wait_for(lambda: sdc.samples.get_state(sample_id) == 'ACTIVE')

    wait_for(lambda: sdc.collection_exercises.get_state(exercise_id) in [
        'READY_FOR_REVIEW'])

    sdc.collection_exercises.execute(exercise_id)

    wait_for(lambda: sdc.collection_exercises.get_state(exercise_id) in [
        'READY_FOR_LIVE', 'LIVE'])

    today = datetime.date.today().strftime('%d%m%Y')

    print(json.dumps(
        {
            'survey_id': survey_id,
            'collection_exercise_id': exercise_id,
            'collection_exercise_period': exercise_period,
            'sample_size': sample_size,
            'execution_date': today,
        }
    ))


main()
