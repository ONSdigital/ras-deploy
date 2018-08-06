import logging

from sdc.clients.collectionexerciseclient import CollectionExerciseClient


class Actions:
    def __init__(self,
                 collection_exercise_client: CollectionExerciseClient,
                 action_service_client):
        self.action_service_client = action_service_client
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

        self.action_service_client.create_action_rule(
            action_plan_id=b_case_action_plan_id,
            action_type_name='BSNL',
            name=f'BSNL-{trigger_time}',
            description=f'Description for BSNL-{trigger_time}',
            trigger_date_time=trigger_time,
            priority=1
        )

    @staticmethod
    def _get_case_types_from_exercise(collection_exercise):
        case_types = {}
        for case_type in collection_exercise['caseTypes']:
            case_types[case_type['sampleUnitType']] = case_type
        return case_types
