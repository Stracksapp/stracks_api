from stracks_api import levels
import collections
import types

import threading
threadlocal = threading.local()

def set_context(r):
    threadlocal.request = r

def get_context():
    try:
        return threadlocal.request
    except AttributeError:
        return None

def sessionid():
    r = get_context()
    if r:
        return r.session.id
    return None

get_request = get_context ## deprecated
set_request = set_context ##    ,,

class Logger(object):
    """
        The request is where logging is stored on.
    """
    action = None
    entity = None

    @classmethod
    def withAction(cls, action):
        l = cls()
        l.action = action
        return l

    @classmethod
    def withEntity(cls, entity):
        l = cls()
        l.entity = entity
        return l


    @property
    def r(self):
        return get_request()

    #def log(self, msg, *entities, action=None, tags=(),
    #             level=levels.INFO, exception=None, data=None):
    #def log(self, msg, *entities, **kw):
    #    return self._log(msg, level=levels.INFO, **kw)

    def _log(self, msg, *entities, **kw):
        if not self.r:
            return  ## can't do anything without a request

        ## backwards compatibility: allow entities to be explicitly named 
        entities = entities or kw.get('entities', ())
        if not entities and self.entity:
            entities = (self.entity,)

        action = kw.get('action')
        tags = kw.get('tags')
        level = kw.get('level')
        exception = kw.get('exception')
        data = kw.get('data')
        self.r.log(msg, entities=entities, action=action or self.action,
                   tags=tags,
                   level=level, exception=exception, data=data)

    def set_owner(self, owner):
        self.r.set_owner(owner)

    def debug(self, msg, *entities, **kw):
        self._log(msg, level=levels.DEBUG, *entities, **kw)

    def info(self, msg, *entities, **kw):
        self._log(msg, level=levels.INFO, *entities, **kw)

    log = info

    def warning(self, msg, *entities, **kw):
        self._log(msg, level=levels.WARNING, *entities, **kw)

    def error(self, msg, *entities, **kw):
        self._log(msg, level=levels.ERROR, *entities, **kw)

    fatal = error

    def critical(self, msg, *entities, **kw):
        self._log(msg, level=levels.CRITICAL, *entities, **kw)

    def exception(self, msg, *entities, **kw):
        if not kw.get('exception'):
            kw['exception'] = True
        self._log(msg, level=levels.EXCEPTION, *entities, **kw)

default_logger = Logger()

set_owner = default_logger.set_owner

debug = default_logger.debug
info = default_logger.info
log = default_logger.log
warning = default_logger.warning
error = default_logger.error
fatal = default_logger.fatal
critical = default_logger.critical
exception = default_logger.exception
