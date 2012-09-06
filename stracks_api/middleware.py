
try:
    from django.conf import settings
    STRACKS_CONNECTOR = settings.STRACKS_CONNECTOR
except (ImportError, AttributeError):
    STRACKS_CONNECTOR = None
    STRACKS_API = None

from stracks_api.api import API
from stracks_api import client, levels

STRACKS_API = None

if STRACKS_CONNECTOR:
    STRACKS_API = API()

class StracksMiddleware(object):
    def process_request(self, request):
        if not STRACKS_API:
            return

        ##
        ## get useragent, ip, path
        ## fetch session, create one if necessary
        ## create request, store it in local thread storage
        useragent = request.META.get('HTTP_USER_AGENT', 'unknown')
        ip = request.META.get('REMOTE_ADDR', '<none>')
        path = request.get_full_path()
        sess = request.session.get('stracks-session')

        if sess is None:
            sess = STRACKS_API.session()
            request.session['stracks-session'] = sess
        request = sess.request(ip, useragent, path)
        client.set_request(request)

    def process_response(self, request, response):
        if not STRACKS_API:
            return response

        r = client.get_request()

        if r:
            if not request.user.is_anonymous():
                ## if there's an active user then he owns
                ## the request. We need to map it to an
                ## entity
                from django.utils.importlib import import_module
                ueb = getattr(settings, 'USER_ENTITY_BUILDER', None)
                if ueb:
                    ## XXX error handling
                    modstr, func = settings.USER_ENTITY_BUILDER.rsplit('.', 1)
                    mod = import_module(modstr)
                    f = getattr(mod, func)
                    r.set_owner(f(request.user))

            r.end()
            client.set_request(None)
        return response

    def process_exception(self, request, exception):
        if not STRACKS_API:
            return
        client.exception("Crash: %s" % exception)

