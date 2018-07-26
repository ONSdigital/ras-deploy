from sdc.clients.http.httpcodeexception import HTTPCodeException
import os
import logging
import requests

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


class CollectionInstrumentClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def upload_collection_instrument(self, survey_id, survey_classifiers):
        upload_params = {'survey_id': survey_id, 'classifiers': survey_classifiers}
        url = collection_instrument_url + collection_instrument_upload_endpoint

        response = requests.post(url=url, params=upload_params, auth=(self.username, self.password))

        if response.status_code != requests.codes.ok:
            raise HTTPCodeException(response.codes.ok, response.status_code,
                                    f'Failed to set collection instrument: {response.text}')

    def link_collection_instrument_to_collection_exercise(self, instrument_id, exercise_id):

        url = f'{collection_instrument_url}{collection_instrument_link_endpoint}/{instrument_id}/{exercise_id}'

        response = requests.post(url=url, auth=(self.username, self.password))

        if response.status_code != requests.codes.ok:
            raise HTTPCodeException(response.codes.ok, response.status_code,
                                    f'Failed to link collection instrument to exercise: {response.text}')

        logging.info('Collection instrument linked to exercise!')

    def get_collection_id_from_classifier(self, classifiers):
        search_params = {'searchString': classifiers}
        url = collection_instrument_url + collection_instrument_search_endpoint

        response = requests.get(url=url, params=search_params, auth=(self.username, self.password))

        if response.status_code != requests.codes.ok:
            raise HTTPCodeException(response.codes.ok, response.status_code,
                                    f'Failed to check for collection instrument: {response.text}')

        results = response.json()
        return results[0]['id'] if len(results) > 0 else None
