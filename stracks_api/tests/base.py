from stracks_api.api import Request

class Testable(object):
    def __init__(self, *args, **kw):
        super(Testable, self).__init__(*args, **kw)
        self._r = Request(None, "1.2.3.4", "test-client", "/test")

    @property
    def r(self):
        return self._r
