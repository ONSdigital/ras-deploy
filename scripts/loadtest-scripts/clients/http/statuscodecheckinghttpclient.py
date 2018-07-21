from clients.http.authenticatedhttpclient import AuthenticatedHTTPClient
from clients.http.httpcodeexception import HTTPCodeException


class StatusCodeCheckingHTTPClient:
    EXPECTED_STATUS_KEY = 'expected_status'

    def __init__(self, client: AuthenticatedHTTPClient):
        self.client = client

    def get(self, **kwargs):
        args = kwargs.copy()

        has_status_code_expectation = self.EXPECTED_STATUS_KEY in kwargs

        if has_status_code_expectation:
            del args[self.EXPECTED_STATUS_KEY]
            expected_status_code = kwargs[self.EXPECTED_STATUS_KEY]

        response = self.client.get(**args)

        if has_status_code_expectation and response.status_code != expected_status_code:
            raise HTTPCodeException(
                kwargs[self.EXPECTED_STATUS_KEY],
                response.status_code,
                f'GET {kwargs["url"]} returned an unexpected '
                f'status code {response.status_code} '
                f'(expected {expected_status_code}): {response.text}')

        return response

    def post(self, **kwargs):
        args = kwargs.copy()

        has_status_code_expectation = self.EXPECTED_STATUS_KEY in kwargs

        if has_status_code_expectation:
            del args[self.EXPECTED_STATUS_KEY]
            expected_status_code = kwargs[self.EXPECTED_STATUS_KEY]

        response = self.client.post(**args)

        if has_status_code_expectation and response.status_code != expected_status_code:
            raise HTTPCodeException(
                kwargs[self.EXPECTED_STATUS_KEY],
                response.status_code,
                f'POST {kwargs["url"]} returned an unexpected '
                f'status code {response.status_code} '
                f'(expected {expected_status_code}): {response.text}')

        return response
