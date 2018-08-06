class CaseServiceClient(object):
    def __init__(self, http_client):
        self.http_client = http_client

    def find_by_iac(self, iac):
        response = self.http_client.get(path=f'/cases/iac/{iac}',
                                        expected_status=200)
        return response.json()