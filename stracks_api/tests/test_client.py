from stracks_api.tests.base import Testable
from stracks_api.api import Logger, Entity
from stracks_api import levels

class TestableLogger(Testable, Logger):
    pass

class TestClient(object):
    """
        Test the client api
    """
    def setup(self):
        self.log = TestableLogger()

    def test_entities(self):
        """ oldstyle keyword entities """
        e = Entity("thingy")
        self.log.log("? bla ?", e(1), e(2))
        assert len(self.log.r.entries) == 1
        assert len(self.log.r.entries[0]['entities']) == 2
        assert self.log.r.entries[0]['entities'] == (e(1), e(2))

    def test_entities_oldstyle(self):
        """ oldstyle keyword entities """
        e = Entity("thingy")
        self.log.log("? bla ?", entities=(e(1), e(2)))
        assert len(self.log.r.entries) == 1
        assert len(self.log.r.entries[0]['entities']) == 2
        assert self.log.r.entries[0]['entities'] == (e(1), e(2))

    def test_levels(self):
        log = TestableLogger()
        def test_level(m, l):
            m("test %d" % l)
            assert log.r.entries[-1]['level'] == l

        for method, level in ((log.debug, levels.DEBUG),
                              (log.info, levels.INFO),
                              (log.log, levels.INFO),
                              (log.warning, levels.WARNING),
                              (log.error, levels.ERROR),
                              (log.critical, levels.CRITICAL),
                              (log.exception, levels.EXCEPTION)):
            yield test_level, method, level

    def test_exception(self):
        try:
            raise ValueError("magic-marker-123")
        except ValueError:
            self.log.exception("Something went wrong")

        assert len(self.log.r.entries) == 1
        assert 'magic-marker-123' in self.log.r.entries[0]['exception']
