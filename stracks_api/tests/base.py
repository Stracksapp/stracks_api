from stracks_api.api import Request
from stracks_api.connector import Connector

class Testable(object):
    def __init__(self, *args, **kw):
        super(Testable, self).__init__(*args, **kw)
        self._r = Request(None, "1.2.3.4", "test-client", "/test")

    @property
    def r(self):
        return self._r


class DummyConnector(Connector):
    def __init__(self):
        self._log = []

    def send(self, data):
        self._log.append(data)

    def transcription(self):
        return self._log

    def clear(self):
        self._log = []
