from stracks_api.api import API, Request
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

    def session_start(self, session_id):
        self._log.append(dict(action="session_start",
                              sessionid=session_id))

    def session_end(self, session_id):
        self._log.append(dict(action="session_end",
                              sessionid=session_id))

    def request(self, session_id, requestdata):
        self._log.append(dict(action="request",
                              sessionid=session_id,
                              data=requestdata))

    def transcription(self):
        return self._log

    def clear(self):
        self._log = []

class APIBase(object):
    def setup(self):
        self.connector = DummyConnector()
        self.api = API(self.connector)

    def get_entry(self):
        """ Retrieve the first (only) entry from the request """
        return self.connector.transcription()[1]['data']['entries'][0]


class RequestBase(APIBase):
    def setup(self):
        super(RequestBase, self).setup()
        self.session = self.api.session()
        self.request = self.session.request('1.2.3.4', 'test agent', '/')
