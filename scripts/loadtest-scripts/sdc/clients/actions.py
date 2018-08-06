import logging

from sdc.clients.collectionexerciseclient import CollectionExerciseClient
from sdc.clients.http.statuscodecheckinghttpclient import StatusCodeCheckingHTTPClient


class Actions:
    def __init__(self, http_client: StatusCodeCheckingHTTPClient,
                 collection_exercise_client: CollectionExerciseClient):
        self.http_client = http_client
        self.collection_exercise_client = collection_exercise_client

    def add_rule_for_collection_exercise(self, exercise_id, trigger_time):
        logging.info(
            'Finding action plan ID for collection exercise {exercise_id}')
        collection_exercise = self.collection_exercise_client.get_by_id(
            exercise_id)

        case_types = self._get_case_types_from_exercise(collection_exercise)
        b_case_action_plan_id = case_types['B']['actionPlanId']
        logging.info(f'Found B case action plan ID: {b_case_action_plan_id}')

        logging.info(f'Creating action rule with 0 day offset')

        iso_trigger_time = trigger_time.strftime("%Y-%m-%dT%H:%M:00.000+0000")
        action_rule = {'actionPlanId': b_case_action_plan_id,
                       'actionTypeName': 'BSNL',
                       'name': f'BSNL-{iso_trigger_time}',
                       'description': f'Description for BSNL-{iso_trigger_time}',
                       'triggerDateTime': iso_trigger_time,
                       'priority': 1}

        logging.debug(f'Creating new action rule {action_rule}')

        self.http_client.post(path='/actionrules',
                              expected_status=201,
                              json=action_rule)

    @staticmethod
    def _get_case_types_from_exercise(collection_exercise):
        case_types = {}
        for case_type in collection_exercise['caseTypes']:
            case_types[case_type['sampleUnitType']] = case_type
        return case_types
