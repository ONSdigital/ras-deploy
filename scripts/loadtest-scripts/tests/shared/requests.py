from requests import Response


class Requests:
    @staticmethod
    def http_response(status_code, body=''):
        response = Response()
        response.status_code = status_code
        response.encoding = 'utf-8'
        response._content = body
        return response