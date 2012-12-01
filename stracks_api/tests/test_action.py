from stracks_api.api import Action, API
from stracks_api.tests.base import Testable, DummyConnector


class TestableAction(Testable, Action):
    pass


class TestAction(object):
    """ basic action tests """
    def setup(self):
        self.connector = DummyConnector()
        self.api = API(self.connector)
        self.r = self.api.session().request("1.2.3.4", "test agent", "/")

    def test_basic(self):
        t = TestableAction("foo")
        assert t() == dict(action="foo")

    def test_called(self):
        """ An action is callable, but when passing to
            the api it doesn't have to be called explicitly """
        t = TestableAction("foo")
        self.r.log("test", action=t())
        self.r.end()
        ## dry TestEntry
        e = self.connector.transcription()[1]['data']['entries'][0]
        assert e['action'] == t()


    def test_notcalled(self):
        """ An action is callable, but when passing to
            the api it doesn't have to be called explicitly """
        t = TestableAction("foo")
        self.r.log("test", action=t)
        self.r.end()
        ## dry TestEntry
        e = self.connector.transcription()[1]['data']['entries'][0]
        assert e['action'] == t()

class TestActionClient(object):
    """
        Test an action being used as a logging client
    """
    def test_default(self):
        a = TestableAction("do_something")
        a.log("Hello World")
        assert len(a.r.entries) == 1
        assert a.r.entries[0]['action'] == a()

    def test_override(self):
        a = TestableAction("do_something")
        b = Action("something_else")
        a.log("Hello World", action=b)
        assert len(a.r.entries) == 1
        assert a.r.entries[0]['action'] == b
