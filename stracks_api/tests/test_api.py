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
        s = self.api.session()
        s.end()
        data = self.connector.transcription()
        assert len(data) == 2
        assert data[0].get('action') == 'session_start'
        assert data[0]['sessionid'] == s.id
        assert data[1].get('action') == 'session_end'


    def test_multiple_session(self):
        self.api.session().end()
        self.api.session().end()
        data = self.connector.transcription()
        assert len(data) == 4
        assert data[0].get('action') == 'session_start'
        assert data[1].get('action') == 'session_end'
        assert data[2].get('action') == 'session_start'
        assert data[3].get('action') == 'session_end'

        assert data[0].get('sessionid') != data[2].get('sessionid')

    def test_single_request(self):
        s = self.api.session()
        s.request("1.2.3.4", "mozilla", "/foo/bar").end()
        s.end()
        data = self.connector.transcription()
        assert len(data) == 3
        assert data[1].get('action') == "request"
        assert data[1].get('sessionid') == s.id
        request = data[1].get('data', {})
        assert request['ip'] == "1.2.3.4"
        assert request['useragent'] == "mozilla"
        assert request['path'] == "/foo/bar"
        assert 'time' in request

    def test_multiple_requests(self):
        s = self.api.session()
        s.request("1.2.3.4", "mozilla", "/foo/bar").end()
        s.request("1.2.3.4", "mozilla", "/foo/blah").end()
        s.end()
        data = self.connector.transcription()
        assert len(data) == 4
        assert data[1]['data']['path'] == '/foo/bar'
        assert data[2]['data']['path'] == '/foo/blah'

    def test_single_entry_simple(self):
        s = self.api.session()
        r = s.request("1.2.3.4", "mozilla", "/foo/bar")
        r.log("hello world")
        r.end()
        s.end()
        data = self.connector.transcription()
        assert len(data) == 3
        assert len(data[1]['data']['entries']) == 1
        e = data[1]['data']['entries'][0]
        assert "msg" in e
        assert "level" in e
        assert "entities" in e
        assert "tags" in e
        assert "action" in e
        assert e['msg'] == "hello world"


