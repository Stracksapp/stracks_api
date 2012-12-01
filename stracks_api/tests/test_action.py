from stracks_api.api import Action
from stracks_api.tests.base import Testable

class TestableAction(Testable, Action):
    pass


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
