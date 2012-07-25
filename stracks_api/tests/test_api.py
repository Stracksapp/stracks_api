from stracks_api.api import Connector, API

class DummyConnector(Connector):
    def __init__(self):
        self._log = []

    def send(self, data):
        self._log.append(data)

    def transcription(self):
        return self._log

    def clear(self):
        self._log = []

class TestAPI(object):
    def setup(self):
        self.connector = DummyConnector()
        self.api = API(self.connector)

    def test_single_session(self):
        s = self.api.session("app-1")
        s.end()
        data = self.connector.transcription()
        assert len(data) == 1       # 1 entry
        entry = data[0]
        assert 'app' in entry
        assert entry['app'] == "app-1"
        assert 'requests' in entry
        assert entry['requests'] == []

    def test_multiple_session(self):
        self.api.session("app-1").end()
        self.api.session("app-2").end()
        data = self.connector.transcription()
        assert len(data) == 2
        assert data[0]['app'] == "app-1"
        assert data[1]['app'] == "app-2"

    def test_single_request(self):
        s = self.api.session("app-1")
        r = s.request("1.2.3.4", "mozilla", "/foo/bar")
        s.end()
        data = self.connector.transcription()
        assert len(data) == 1       # 1 request
        entry = data[0]
        assert len(entry['requests']) == 1
        request = entry['requests'][0]
        assert request['ip'] == "1.2.3.4"
        assert request['useragent'] == "mozilla"
        assert request['path'] == "/foo/bar"
        assert 'time' in request

    def test_multiple_requests(self):
        s = self.api.session("app-1")
        s.request("1.2.3.4", "mozilla", "/foo/bar")
        s.request("1.2.3.4", "mozilla", "/foo/blah")
        s.end()
        data = self.connector.transcription()
        assert len(data) == 1       # 1 session
        assert data[0]['requests'][0]['path'] == '/foo/bar'
        assert data[0]['requests'][1]['path'] == '/foo/blah'

    def test_single_entry_simple(self):
        s = self.api.session("app-1")
        r = s.request("1.2.3.4", "mozilla", "/foo/bar")
        r.log("hello world")
        s.end()
        data = self.connector.transcription()
        assert len(data) == 1
        assert len(data[0]['requests'][0]['entries']) == 1
        e = data[0]['requests'][0]['entries'][0]
        assert "msg" in e
        assert "level" in e
        assert "entities" in e
        assert "tags" in e
        assert "action" in e
        assert e['msg'] == "hello world"


