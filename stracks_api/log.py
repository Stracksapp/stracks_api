import threading
threadlocal = threading.local()

def set_request(r):
    threadlocal.request = r

def get_request():
    try:
        return threadlocal.request
    except AttributeError:
        return None

def log(msg, entities=()):
    r = get_request()
    if r:
        r.log(msg, entities=entities)
