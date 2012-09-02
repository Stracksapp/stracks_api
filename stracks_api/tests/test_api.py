from stracks_api.api import API, Entity, Action
from stracks_api.connector import Connector

from stracks_api import levels
from stracks_api.util import parse_dt

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
        assert 'started' in request
        assert 'ended' in request

        ## verify it's a parsable string
        assert parse_dt(request['started'])
        assert parse_dt(request['ended'])

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

class TestEntry(object):
    """
        Test the different aspects of entry logging
        (entities, tags)
    """
    def setup(self):
        self.connector = DummyConnector()
        self.api = API(self.connector)
        self.session = self.api.session()
        self.request = self.session.request('1.2.3.4', 'test agent', '/')

    def get_entry(self):
        """ Retrieve the first (only) entry from the request """
        return self.connector.transcription()[1]['data']['entries'][0]

    def test_msg(self):
        self.request.log("Hello World")
        self.request.end()
        entry = self.get_entry()
        assert 'msg' in entry
        assert entry['msg'] == "Hello World"
        assert entry['level'] == levels.INFO

    def test_level(self):
        self.request.log("Hello World", level=levels.DEBUG)
        self.request.end()
        entry = self.get_entry()
        assert entry['level'] == levels.DEBUG

    def test_entity(self):
        """ test a single entity """
        self.request.log("Hello World", entities=(Entity(1337)(12, "Demo"),))
        self.request.end()
        entry = self.get_entry()
        assert 'entities' in entry
        assert len(entry['entities']) == 1
        assert entry['entities'][0] == dict(entity=1337, id=12, name="Demo")

    def test_entities(self):
        """ test multiple entities """
        self.request.log("Hello World", entities=(Entity(1337)(12, "Demo"),
                                                  Entity(42)(1337)))
        self.request.end()
        entry = self.get_entry()
        assert 'entities' in entry
        assert len(entry['entities']) == 2
        assert entry['entities'][0] == dict(entity=1337, id=12, name="Demo")
        assert entry['entities'][1] == dict(entity=42, id=1337, name=None)

    def test_no_action(self):
        """ test missing (optional) action """
        self.request.log("Hello World")
        self.request.end()
        entry = self.get_entry()
        assert entry['action'] is None

    def test_action(self):
        """ test missing (optional) action """
        self.request.log("Hello World", level=levels.DEBUG, action=Action(42)())
        self.request.end()
        entry = self.get_entry()
        assert entry['action'] == dict(action=42)

    def test_no_tags(self):
        """ test missing (optional) tags """
        self.request.log("Hello World")
        self.request.end()
        entry = self.get_entry()
        assert len(entry['tags']) == 0

    def test_single_tag(self):
        """ test missing (optional) tags """
        self.request.log("Hello World", tags=["tag1"])
        self.request.end()
        entry = self.get_entry()
        assert len(entry['tags']) == 1
        assert entry['tags'][0] == "tag1"

    def test_multiple_tags(self):
        """ test missing (optional) tags """
        self.request.log("Hello World", tags=["tag1", "tag2"])
        self.request.end()
        entry = self.get_entry()
        assert len(entry['tags']) == 2
        assert entry['tags'][0] == "tag1"
        assert entry['tags'][1] == "tag2"

class TestClient(object):
    """
        Test the client api
    """

