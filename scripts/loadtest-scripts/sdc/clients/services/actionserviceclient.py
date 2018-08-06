import logging


class ActionServiceClient:
    ISO_TIME_FORMAT = '%Y-%m-%dT%H:%M:00.000+0000'

    def __init__(self, http_client):
        self.http_client = http_client

    def create_action_rule(self,
                           action_plan_id,
                           action_type_name,
                           name,
                           description,
                           trigger_date_time,
                           priority):

        iso_trigger_time = trigger_date_time.strftime(self.ISO_TIME_FORMAT)

        action_rule = {'actionPlanId': action_plan_id,
                       'actionTypeName': action_type_name,
                       'name': name,
                       'description': description,
                       'triggerDateTime': iso_trigger_time,
                       'priority': priority}

        logging.debug(f'Creating new action rule {action_rule}')

        self.http_client.post(path='/actionrules',
                              expected_status=201,
                              json=action_rule)