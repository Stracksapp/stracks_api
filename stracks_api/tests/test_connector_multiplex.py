from stracks_api.connector import MultiplexConnector, UnknownAction
from stracks_api.tests.base import DummyConnector

import pytest

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

    def test_session_end(self):
        session_id = "test_session"

        self.connector.send(dict(action="request",
                                 sessionid=session_id,
                                 data="random data"))

        for c in self.connectors:
            assert c.transcription()[0].get('action') == 'request'
            assert c.transcription()[0].get('sessionid') == session_id

    def test_request(self):
        session_id = "test_session"

        self.connector.send(dict(action="session_end",
                                 sessionid=session_id))

        for c in self.connectors:
            assert c.transcription()[0].get('action') == 'session_end'
            assert c.transcription()[0].get('sessionid') == session_id

    def test_invalid_command(self):
        session_id = "test_session"

        ## the first connector will raise
        pytest.raises(UnknownAction,
                      self.connector.send,
                      dict(action="non-existend-action",
                           sessionid=session_id)
                     )

        for c in self.connectors:
            assert c.transcription() == []

class TestSingleMultiplex(BaseMultiplexTest):
    def setup_connectors(self):
        return [DummyConnector()]


class TestDualMultiplex(BaseMultiplexTest):
    def setup_connectors(self):
        return [DummyConnector(), DummyConnector()]


class TestTripleMultiplex(BaseMultiplexTest):
    def setup_connectors(self):
        return [DummyConnector(), DummyConnector(), DummyConnector()]
