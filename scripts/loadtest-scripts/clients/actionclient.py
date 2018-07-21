from clients.collectionexerciseclient import CollectionExerciseClient
from clients.http.statuscodecheckinghttpclient import StatusCodeCheckingHTTPClient


class ActionClient:
    def __init__(self, http_client: StatusCodeCheckingHTTPClient,
                 collection_exercise_client: CollectionExerciseClient):
        self.http_client = http_client
        self.collection_exercise_client = collection_exercise_client

    def add_action_rule_to_collection_exercise(self, exercise_id):
        collection_exercise = self.collection_exercise_client.get_collection_exercise(
            exercise_id)

        case_types = self._get_case_types_from_exercise(collection_exercise)

        b_case_action_plan_id = case_types['B']['actionPlanId']

        self.http_client.post(path='/actionrules',
                              expected_status=201,
                              json={
                                  "actionPlanId": b_case_action_plan_id,
                                  "actionTypeName": "BSNL",
                                  "name": "BSNL+0",
                                  "description": "Description for BSNL+0",
                                  "daysOffset": 0,
                                  "priority": 1})

    @staticmethod
    def _get_case_types_from_exercise(collection_exercise):
        case_types = {}
        for case_type in collection_exercise['caseTypes']:
            case_types[case_type['sampleUnitType']] = case_type
        return case_types
