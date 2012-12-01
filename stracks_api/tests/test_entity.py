from stracks_api.api import Entity
from stracks_api.tests.base import Testable


class TestableEntity(Entity):
    class instance_class(Testable, Entity.instance_class):
        pass

class TestEntityClient(object):
    """
        Test an entity being used as a logging client
    """
    def test_default(self):
        a = TestableEntity("something")("someone")
        a.log("Hello World")
        assert len(a.r.entries) == 1
        assert a.r.entries[0]['entities'][0]['entity'] == "something"

    def test_override(self):
        """ entity itself remains first/primary entity, others
            are appended """
        a = TestableEntity("something")("someone")
        a.log("Hello World", entities=(Entity("other")("abc"),))
        assert len(a.r.entries) == 1
        entities = a.r.entries[0]['entities']

        assert entities[0]['entity'] == "something"
        assert entities[1]['entity'] == "other"
