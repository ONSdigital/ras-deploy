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
sample_url = \
    os.getenv('SAMPLE_URL',
              'http://localhost:8125')
collection_exercise_url = \
    os.getenv('COLLECTION_EXERCISE_URL', 'http://localhost:8145')
survey_id = os.getenv('SURVEY_ID', '75b19ea0-69a4-4c58-8d7f-4458c8f43f5c')
classifiers = os.getenv('SURVEY_CLASSIFIERS', '{"form_type":"0102","eq_id":"1"}')
username = os.getenv('COLLECTION_INSTRUMENT_USERNAME', 'admin')
password = os.getenv('COLLECTION_INSTRUMENT_PASSWORD', 'secret')

search_params = {'searchString': classifiers}
upload_params = {'survey_id': survey_id, 'classifiers': classifiers}


def check_for_collection_instruments():
    response = requests.get(collection_instrument_url + collection_instrument_search_endpoint,
                            params=search_params,
                            auth=(username, password))
    if response.status_code != requests.codes.ok:
        print(f'Failed to check for collection instrument: {response.text}')
        exit(1)
    else:
        return len(response.json()) > 0


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
        print(f'Failed fetch collection exercises for survey {survey_id}: {response.text}')
        exit(1)

    exercises = response.json()

    exercise = get_collection_exercise_by_period(exercises, period)

    if exercise is None:
        print(f'No collection exercise found for period {period} of {survey_id}')
        exit(1)

    return exercise['id']

def link_sample_to_collection_exercise(sample_id, exercise_id):
    url = f'{collection_exercise_url}/collectionexercises/link/{exercise_id}'
    payload = {"sampleSummaryIds": [str(sample_id)]}

    response = requests.put(url, auth=(username, password), json=payload)
    if response.status_code != requests.codes.ok:
        print(f'Failed to link sample to collection exercise: {response.text}')
        exit(1)
    else:
        print('Sample linked to collection exercise!')

def upload_collection_instrument():
    response = requests.post(collection_instrument_url + collection_instrument_upload_endpoint,
                             params=upload_params,
                             auth=(username, password))
    if response.status_code != requests.codes.ok:
        print(f'Failed to set collection instrument: {response.text}')
        exit(1)
    else:
        print(f'Collection instrument set!')

def upload_sample_file(file_path):
    survey_type = 'B'
    url = f'{sample_url}/samples/{survey_type}/fileupload'
    response = requests.post(url=url,
                             auth=(username, password),
                             files={'file': open(file_path, 'rb')})

    if response.status_code != requests.codes.created:
        print(f'Failed to upload sample file: {response.text}')
        exit(1)

    return response.json()['id']

def main():
    if not check_for_collection_instruments():
        upload_collection_instrument()
    else:
        print('Collection instrument exists; skipping')

    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = f'{script_dir}/sample.csv'

    # if there_is_already_an_uploaded_sample???
    sample_id = upload_sample_file(file_path)
    print(f'Sample ID = {sample_id}')
    period = get_previous_period()
    print(f'Fetching collection exercise for {period}')
    exercise_id = get_collection_exercise_id(survey_id, period)
    print(f'Exercise ID = {exercise_id}')

    link_sample_to_collection_exercise(sample_id, exercise_id)

main()

# Delete me!
# def _upload_sample(short_name, period):
#     error = _validate_sample()
#
#     if not error:
#         survey = survey_controllers.get_survey_by_shortname(short_name)
#         exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey['id'])
#
#         # Find the collection exercise for the given period
#         exercise = get_collection_exercise_by_period(exercises, period)
#
#         if not exercise:
#             return make_response(jsonify({'message': 'Collection exercise not found'}), 404)
#         sample_summary = sample_controllers.upload_sample(short_name, period, request.files['sampleFile'])
#
#         logger.info('Linking sample summary with collection exercise',
#                     collection_exercise_id=exercise['id'],
#                     sample_id=sample_summary['id'])
#
#         collection_exercise_controllers.link_sample_summary_to_collection_exercise(
#             collection_exercise_id=exercise['id'],
#             sample_summary_id=sample_summary['id'])
#
#     return redirect(url_for('collection_exercise_bp.view_collection_exercise', short_name=short_name, period=period,
#                             error=error, show_msg='true'))
