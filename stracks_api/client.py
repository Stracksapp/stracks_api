from stracks_api import levels
import collections
import types

import threading
threadlocal = threading.local()

def set_request(r):
    threadlocal.request = r

def get_request():
    try:
        return threadlocal.request
    except AttributeError:
        return None

class Logger(object):
    """
        The request is where logging is stored on.
    """
    @property
    def r(self):
        return get_request()

    def __call__(self, msg, entities=(), action=None, tags=(),
                 level=levels.INFO, exception=None, data=None):
        if not self.r:
            return  ## can't do anything without a request

        if not isinstance(entities, collections.Iterable) \
            or isinstance(entities, types.StringTypes):
            entities = (entities,)

        self.r.log(msg, entities=entities, action=action, tags=tags,
                   level=level, exception=exception, data=data)

    def set_owner(self, owner):
        self.r.set_owner(owner)

logger = Logger()

def set_owner(u):
    logger.set_owner(u)

def debug(msg, entities=(), action=None, tags=(), exception=None, data=None):
    logger(msg, entities=entities, action=action, tags=tags,
         level=levels.DEBUG, exception=exception, data=data)

def info(msg, entities=(), action=None, tags=(), exception=None, data=None):
    logger(msg, entities=entities, action=action, tags=tags,
         level=levels.INFO, exception=exception, data=data)

log = info
def warning(msg, entities=(), action=None, tags=(), exception=None, data=None):
    logger(msg, entities=entities, action=action, tags=tags,
         level=levels.WARNING, exception=exception, data=data)

def error(msg, entities=(), action=None, tags=(), exception=None, data=None):
    logger(msg, entities=entities, action=action, tags=tags,
         level=levels.ERROR, exception=exception, data=data)

fatal = error

def critical(msg, entities=(), action=None, tags=(), exception=None, data=None):
    logger(msg, entities=entities, action=action, tags=tags,
         level=levels.CRITICAL, exception=exception, data=data)

def exception(msg, entities=(), action=None, tags=(), exception=None, data=None):
    """ if no exception is specified default to True """
    logger(msg, entities=entities, action=action, tags=tags,
         level=levels.EXCEPTION, exception=exception or True, data=data)

