import requests
import os

search_url = os.getenv('COLLECTION_INSTRUMENT_SEARCH_URL',
                       'http://ras-collection-instrument-sit.apps.devtest.onsclofo.uk/'
                       'collection-instrument-api/1.0.2/collectioninstrument')
upload_url = os.getenv('COLLECTION_INSTRUMENT_UPLOAD_URL',
                       'http://ras-collection-instrument-sit.apps.devtest.onsclofo.uk/'
                       'collection-instrument-api/1.0.2/upload')
survey_id = os.getenv('SURVEY_ID', '75b19ea0-69a4-4c58-8d7f-4458c8f43f5c')
classifiers = os.getenv('SURVEY_CLASSIFIERS', '{"form_type":"0102","eq_id":"1"}')
username = os.getenv('COLLECTION_INSTRUMENT_API_USERNAME', 'sdc.loadtest')
password = os.getenv('COLLECTION_INSTRUMENT_API_PASSWORD', 'firm.wing.weather.legs.opinion.capital')

search_params = {'searchString': classifiers}
upload_params = {'survey_id': survey_id, 'classifiers': classifiers}


def check_for_collection_instruments():
    response = requests.get(search_url, params=search_params, auth=(username, password))
    if response.status_code != requests.codes.ok:
        print("Failed to check for collection instrument: " + response.text)
        exit(1)
    else:
        return len(response.json()) > 0


def upload_collection_instrument():
    response = requests.post(upload_url, params=upload_params, auth=(username, password))
    if response.status_code != requests.codes.ok:
        print("Failed to set collection instrument: " + response.text)
        exit(1)
    else:
        print("Collection instrument set!")
        exit(0)


if not check_for_collection_instruments():
    upload_collection_instrument()
else:
    print("Collection instrument exists; skipping")
