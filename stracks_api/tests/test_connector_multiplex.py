from stracks_api.connector import MultiplexConnector
from stracks_api.tests.base import DummyConnector


class BaseMultiplexTest(object):
    def setup_connectors(self):
        return []

    def setup(self):
        self.connectors = self.setup_connectors()
        self.connector = MultiplexConnector(*self.connectors)

    def test_session_start(self):
        session_id = "test_session"

        self.connector.send(dict(action="session_start",
                                 sessionid=session_id))

        for c in self.connectors:
            assert c.transcription()[0].get('action') == 'session_start'
            assert c.transcription()[0].get('sessionid') == session_id

class TestSingleMultiplex(BaseMultiplexTest):
    def setup_connectors(self):
        return [DummyConnector()]


class TestDualMultiplex(BaseMultiplexTest):
    def setup_connectors(self):
        return [DummyConnector(), DummyConnector()]


class TestTripleMultiplex(BaseMultiplexTest):
    def setup_connectors(self):
        return [DummyConnector(), DummyConnector(), DummyConnector()]
