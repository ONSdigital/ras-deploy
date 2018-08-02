import json
import logging
import os
import sys

from sdc.clients import SDCClient, sdcclient
from sdc.clients.iac_client import RemoteFileNotFoundException
from sdc.utils import wait_for, logger

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

logger.initialise_from_env()


def download_iac_codes(sdc_client, period, expected_codes, today):
    try:
        return sdc_client.iac_codes.download(
            period=period,
            generated_date=today,
            expected_codes=expected_codes)

    except RemoteFileNotFoundException:
        return None


def main():
    if len(sys.argv) is not 2:
        print(f'Usage: {sys.argv[0]} config_file')
        exit(1)

    with open(sys.argv[1], 'r') as file:
        exercise_config = json.load(file)

    logging.debug(f'Exercise config loaded: {exercise_config}')

    sdc = SDCClient(sdcclient.config_from_env())

    iac_codes = wait_for(lambda: download_iac_codes(
        sdc_client=sdc,
        period=exercise_config['collection_exercise_period'],
        expected_codes=exercise_config['sample_size'],
        today=exercise_config['execution_date']))

    print(iac_codes)


main()
