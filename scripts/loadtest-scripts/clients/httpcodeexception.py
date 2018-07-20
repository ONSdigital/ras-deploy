class HTTPCodeException(Exception):
    def __init__(self, expected, received, message):
        self.expected = expected
        self.received = received
        self.message = message