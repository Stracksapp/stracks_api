import threading
threadlocal = threading.local()

def set_request(r):
    threadlocal.request = r

def get_request():
    try:
        return threadlocal.request
    except AttributeError:
        return None

def log(msg, entities=(), action=None):
    ## if msg contains a single ? and / ror entities a single element,
    ## we might support that.
    ## log("Hello ?", user(..), hello_action)

    r = get_request()
    if r:
        r.log(msg, entities=entities, action=action)
