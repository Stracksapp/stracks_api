from stracks_api import levels

import threading
threadlocal = threading.local()

def set_request(r):
    threadlocal.request = r

def get_request():
    try:
        return threadlocal.request
    except AttributeError:
        return None

def debug(msg, entities=(), action=None, tags=()):
    _log(msg, entities, action, tags, levels.DEBUG)

def log(msg, entities=(), action=None, tags=()):
    _log(msg, entities, action, tags, levels.INFO)

def _log(msg, entities=(), action=None, tags=(), level=levels.INFO):
    ## handle non-sequence entitites
    try:
        entities[0]
    except IndexError:
        entities = (entities,)

    r = get_request()
    if r:
        r.log(msg, entities=entities, action=action)
