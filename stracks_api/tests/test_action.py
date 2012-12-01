from stracks_api.api import Action
from stracks_api.tests.base import Testable, RequestBase


class TestableAction(Testable, Action):
    pass


class TestAction(RequestBase):
    """ basic action tests """
    def test_basic(self):
        t = TestableAction("foo")
        assert t() == dict(action="foo")

    def test_called(self):
        """ An action is callable, but when passing to
            the api it doesn't have to be called explicitly """
        t = TestableAction("foo")
        self.request.log("test", action=t())
        self.request.end()
        e = self.get_entry()
        assert e['action'] == t()


    def test_notcalled(self):
        """ An action is callable, but when passing to
            the api it doesn't have to be called explicitly """
        t = TestableAction("foo")
        self.request.log("test", action=t)
        self.request.end()
        e = self.get_entry()
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
        assert a.r.entries[0]['action'] == b()
